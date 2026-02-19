import pyvisa
import zmq
from .psu_queue import PSUQueue
from .PSU import PSU
from logger import setup_logger

logger = setup_logger(name="server")

class Server:
    """A server to handle client requests for PSU control via SCPI commands over ZeroMQ."""

    def __init__(self, config, address="tcp://*:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(address)
        self.psu_queues = {}
        self.rm = pyvisa.ResourceManager('psu_sims.yaml@sim')
        self.clients = set()

        self.config = config

        self.psus = {}

    def start(self):
        logger.info("Server started")

        logger.info("Connecting to PSUs with config")

        for name, psu in self.config.items():
            self.connect_psu(psu["address"], name=name)

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

        handler(address=address, identity=identity)


    def handle_scpi_command(self, identity, address, payload):
        if address not in self.psu_queues:
            self.send_error(identity, "PSU not connected", address)
            return

        self.psu_queues[address].add_command(identity, payload)



    def connect_psu(self, address, identity=None, name=None):
        if address in self.psu_queues:
            logger.error(f"PSU {address} already connected")
            self.send_error(identity=identity, message="PSU already connected", address=address)
            return
        try:
            if name:
                logger.debug(f'trying to connect {name}')
                psu = PSU(self.rm.open_resource(address), name=name)
            else:
                psu = PSU(self.rm.open_resource(address))
        except Exception as e:
            logger.error("Could not connect ", address)
        psu.connected = True
        self.psus[address] = psu
        self.psu_queues[address] = PSUQueue(self.psus[address], self)

        logger.info(f'connected psu: {psu.name}')

        if identity:
            self.broadcast_status(address)

            reply = {
                "type": "system_reply",
                "address": address,
                "payload": {
                    "connect": "OK"
                }
            }
            self.send_response(identity, reply)
    
    def disconnect_psu(self, identity, address):
        if address not in self.psu_queues:
            logger.error(f"PSU {address} not connected")
            self.send_error(identity, "PSU not connected", address)
            return
        psu = self.psus[address]
        psu.connected = False
        del self.psu_queues[address]
        logger.info(f'Diconnected PSU {psu.name}')

        self.broadcast_status(address)

        reply = {
            "type": "system_reply",
            "address": address,
            "payload": {
                "disconnect": "OK"
            }
        }

        self.send_response(identity, reply)


    def send_status(self, identity, address):
        psu = self.psus.get(address)
        status_message = {
            "type": "status_update", 
            "status": psu.get_state(), 
            "address": address
        }
        self.send_response(identity, status_message)


    def send_error(self, identity, message, address):
        reply = {
            "type": "error",
            "address": address,
            "payload": {
                "message": message
            }
        }
        self.send_response(identity, reply)

    def broadcast_status(self, address):
        psu = self.psus.get(address)
        status_message = {
            "type": "status_update",
            "address": address,
            "state": psu.get_state()
        }
        self.broadcast(status_message)

    def broadcast(self, message):
        logger.info(f"Broadcasting status update")
        for client in self.clients:
            self.send_response(client, message)

    def send_response(self, identity, response):
        logger.info(f'Sending response {response}')
        self.socket.send(identity, zmq.SNDMORE)
        self.socket.send_json(response)
