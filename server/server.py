import os
import pyvisa
import zmq
from .psu_queue import PSUQueue
from .PSU import PSU
from .requestKomponents import generate_reply, generate_status_update
from logger import setup_logger
from .Translate import HMP4040_dic, get_dic_for_PSU

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
        self.pub = self.context.socket(zmq.PUB)
        self.pub.bind("tcp://*:5556")

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
        # msg_type = request.get("type")
        # self.clients.add(identity)

        # logger.info(f"Received request: {request}")

        # if msg_type == "system_request":
        #     self.handle_system(identity, request)
        # elif msg_type == "scpi_request":
        #     self.handle_scpi(identity, request)
        # else:
        #     logger.error(f"Uknown request type {msg_type}")
        #     raise ValueError("Unknown request type")
        #Nå kommer requestene på denne formaten: set-channel 1, set-output 1
        #Vi må oversette den til en ny request som vi kan sende til PyVisa.
        request = {"name": "HMP4040", "payload": ["set_channel 1", "set_output 1"]}
        pyvisa_request = []
        #Må hente riktig dic for type psu
        dic = get_dic_for_PSU(request["name"])
        for s in request["payload"]:
            #Iterer over requesten og se om den er like noen av verdiene i en json fil vi har som vi kan bruke til å oversette requestene.
            pyvisa_request.append(dic[s.split(" ")])
        print(pyvisa_request)
        
    def handle_system(self, identity, request):
        address = request.get("address")
        actions = request["payload"]

        dispatch = {
            "connect": self.connect_psu,
            "disconnect": self.disconnect_psu,
            "status": self.send_status,
        }
        handler = []
        for action in actions:
            handler.append(dispatch.get(action))
        
        if len(handler) > 0:
            for action in handler:
                action(identity,address)
        else:
            logger.error(f"Uknown system action {action}")
            self.send_error(identity=identity,message= f"Unknown system action: {action}", address=address)

    def handle_scpi(self, identity, request):
        address = request.get("address")

        if address not in self.psu_queues:
            logger.error(f"Uknown instrument address {address}")
            raise ValueError(f"Unknown instrument address: {address}")
        self.psu_queues[address].add_command(identity, request)

    def connect_psu(self, identity, address):
        if address in self.psu_queues:
            logger.error(f"PSU {address} already connected")
            self.send_error(identity=identity, message="PSU already connected", address=address)
            return
        
        psu = PSU(self.rm.open_resource(address))
        psu.connected = True
        self.psus[address] = psu
        self.psu_queues[address] = PSUQueue(self.psus[address], self)

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
        
        logger.info(f"Broadcasting status update {message}")

        for client in self.clients:
            self.send_response(client, message)

    def send_response(self, identity, response):
        logger.info(f'Sending response {response}')
        self.socket.send(identity, zmq.SNDMORE)
        self.socket.send_json(response)
