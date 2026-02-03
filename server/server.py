import pyvisa
import zmq
from psu_queue import PSUQueue
from PSU import PSU

class Server:
    """A server to handle client requests for PSU control via SCPI commands over ZeroMQ."""

    def __init__(self, address="tcp://*:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(address)
        self.psu_queues = {}
        self.rm = pyvisa.ResourceManager('dummy_psu.yaml@sim')
        self.clients = set()
        self.psus = {}

    def start(self):
        print("Server started")
        print("Waiting for requests...")

        while True:
            identity = self.socket.recv()
            request = self.socket.recv_json()

            try:
                self.handle_request(identity, request)
            except Exception as e:
                print(f"Error handling request: {e}")
                self.send_error(identity, str(e))

    def handle_request(self, identity, request):
        msg_type = request.get("type")
        self.clients.add(identity)

        print(f"Received request: {request}")
        print(f"address in request: {request.get('address')}")

        if msg_type == "system_request":
            self.handle_system(identity, request)
        elif msg_type == "scpi_request":
            self.handle_scpi(identity, request)
        else:
            raise ValueError("Unknown request type")
        
    def handle_system(self, identity, request):
        payload = request.get("payload", {})
        action = payload.get("action")
        address = request.get("address")

        dispatch = {
            "connect": self.connect_psu,
            "disconnect": self.disconnect_psu,
            "status": self.send_status,
        }

        handler = dispatch.get(action)
        if handler:
            handler(identity, address)
        else:
            self.send_error(identity, f"Unknown system action: {action}")


    def handle_scpi(self, identity, request):
        address = request.get("address")

        if address not in self.psu_queues:
            raise ValueError(f"Unknown instrument address: {address}")
        self.psu_queues[address].add_command(identity, request)

    def connect_psu(self, identity, address):
        if address in self.psu_queues:
            self.send_error(identity, "PSU already connected")
            return
        
        psu = PSU(self.rm.open_resource(address))
        psu.connected = True
        self.psus[address] = psu
        self.psu_queues[address] = PSUQueue(self.psus[address], self)

        response = {"type": "status_update", "status": psu.get_state(), "address": address}
        self.broadcast(response)
        self.send_response(identity, response)
    
    def disconnect_psu(self, identity, address):
        if address not in self.psu_queues:
            self.send_error(identity, "PSU not connected")
            return
        psu = self.psus[address]
        psu.connected = False
        del self.psu_queues[address]
        response = {"type": "status_update", "status": psu.get_state(), "address": address}
        self.broadcast(response)
        self.send_response(identity, response)
       
    def send_status(self, identity, address):
        psu = self.psus.get(address)
        response = {"type": "status_update", "status": psu.get_state(), "address": address}
        self.send_response(identity, response)

    def send_error(self, identity, message):
        reply = {"type": "error", "message": message}
        self.send_response(identity, reply)

    def broadcast(self, message):
        pass
        # for client in self.clients:
        #     print(f"Broadcasting")
        #     self.send_response(client, message)

    def send_response(self, identity, response):
        print(f"Sending response {response}")
        self.socket.send(identity, zmq.SNDMORE)
        self.socket.send_json(response)
