import pyvisa
import zmq
from .psu_queue import PSUQueue
from .PSU import PSU
from .requestKomponents import generate_reply, generate_status_update
from logger import setup_logger


logger = setup_logger(name="server")

class Server:
    """A server to handle client requests for PSU control via SCPI commands over ZeroMQ."""

    def __init__(self, address="tcp://*:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(address)
        self.psu_queues = {}
        self.rm = pyvisa.ResourceManager('psu_sims.yaml@sim')
        self.clients = set()
        self.psus = {}

    def start(self):
        logger.info("Server started")

        while True:
            identity = self.socket.recv()
            request = self.socket.recv_json()

            try:
                self.handle_request(identity, request)
            except Exception as e:
                logger.error(f"Couldn't handle request. error: {e}")
                self.send_error(identity=identity, message=str(e), address=request.get("address"))

    def handle_request(self, identity, request):
        payload = request.get("payload", {})
        address = request.get("name")

        logger.info(f"received: {request}")

        system_commands = {"connect", "disconnect", "status"}

        for command, value in payload.items():
            if command in system_commands and value:
                self.handle_system_command(identity, address, command)
                return
            

        self.handle_scpi_command(identity, address, payload)

        
    def handle_system_command(self, identity, address, command):
        dispatch = {
            "connect": self.connect_psu,
            "disconnect": self.disconnect_psu,
            "status": self.send_status,
        }

        handler = dispatch.get(command)

        if not handler:
            self.send_error(identity, f"Unknown system command: {command}", address)
            return

        handler(identity, address)


    def handle_scpi_command(self, identity, address, payload):
        if address not in self.psu_queues:
            self.send_error(identity, "PSU not connected", address)
            return

        self.psu_queues[address].add_command(identity, payload)


    def connect_psu(self, identity, address):
        if address in self.psu_queues:
            logger.error(f"PSU {address} already connected")
            self.send_error(identity=identity, message="PSU already connected", address=address)
            return
        
        psu = PSU(self.rm.open_resource(address))
        psu.connected = True
        self.psus[address] = psu
        self.psu_queues[address] = PSUQueue(self.psus[address], self)

        logger.info(f'connected psu: {psu.name}')

        response = generate_status_update(psu.get_state(), address)
        self.broadcast(response)
        self.send_response(identity, response)
    
    def disconnect_psu(self, identity, address):
        if address not in self.psu_queues:
            logger.error(f"PSU {address} not connected")
            self.send_error(identity, "PSU not connected", address)
            return
        psu = self.psus[address]
        psu.connected = False
        del self.psu_queues[address]
        logger.info(f'Diconnected PSU {psu.name}')
        response = generate_status_update(state=psu.get_state(), address=address)
        self.broadcast(response)
        self.send_response(identity, response)

    # endre på noe her for å få vekk error på server-side om en client spør om status uten å være koblet på en psu? <- da er det gjort
    def send_status(self, identity, address):
        psu = self.psus.get(address)
        response = generate_status_update(state=psu.get_state(), address=address)
        self.send_response(identity, response)

    def send_error(self, identity, message, address):
        reply = generate_reply(type="error", address=address, response=message)
        self.send_response(identity, reply)

    def broadcast(self, message):
        
        # logger.info(f"Broadcasting status update {message}")

        for client in self.clients:
            self.send_response(client, message)

    def send_response(self, identity, response):
        logger.info(f'Sending response {response}')
        self.socket.send(identity, zmq.SNDMORE)
        self.socket.send_json(response)
