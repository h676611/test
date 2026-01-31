import pyvisa
import zmq
import json
import queue
import threading


class Server:
    def __init__(self, psu_queues, address="tcp://*:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(address)
        self.psu_queues = psu_queues
        self.rm = pyvisa.ResourceManager('dummy_psu.yaml@sim')
        self.clients = set()

    def start(self):
        print("Server started")
        print("Waiting for requests...")

        while True:
            identity, message = self.socket.recv_multipart()

            try:
                request = json.loads(message.decode())
            except json.JSONDecodeError:
                self.send_error(identity, "Invalid JSON")
                continue

            try:
                self.handle_request(identity, request)
            except Exception as e:
                print(f"Error handling request: {e}")
                self.send_error(identity, str(e))

    def handle_request(self, identity, request):
        msg_type = request.get("type")
        self.clients.add(identity)

        print(f"Received request: {request}")

        if msg_type == "system":
            self.handle_system(identity, request)
        elif msg_type == "scpi":
            self.handle_scpi(identity, request)
        else:
            raise ValueError("Unknown request type")
        
    def handle_system(self, identity, request):
        action = request.get("action")
        address = request.get("address")

        if action == "connect":
            self.connect_psu(identity, address)
        elif action == "disconnect":
            self.disconnect_psu(identity, address)
        elif action == "status":
            status = "connected" if address in self.psu_queues else "disconnected"
            response = {"type": "status_update", "status": status, "address": address}
            self.send_response(identity, json.dumps(response))
        else:
            raise ValueError("Unknown system action")

    def handle_scpi(self, identity, request):
        address = request.get("address")

        if address not in self.psu_queues:
            raise ValueError(f"Unknown instrument address: {address}")
        self.psu_queues[address].add_command(identity, request)

    def connect_psu(self, identity, address):
        if address in self.psu_queues:
            self.send_error(identity, "PSU already connected")
            return
        
        psu = self.rm.open_resource(address)
        self.psu_queues[address] = PSUQueue(psu, self)

        response = {"type": "status_update", "status": "connected", "address": address}
        self.broadcast(json.dumps(response))
        self.send_response(identity, json.dumps(response))
    
    def disconnect_psu(self, identity, address):
        if address not in self.psu_queues:
            self.send_error(identity, "PSU not connected")
            return

        del self.psu_queues[address]
        response = {"type": "status_update", "status": "disconnected", "address": address}
        self.broadcast(json.dumps(response))
        self.send_response(identity, json.dumps(response))
       
    def send_error(self, identity, message):
        reply = {"status": "error", "message": message}
        self.send_response(identity, json.dumps(reply))

    def broadcast(self, message):
        for client in self.clients:
            print(f"Sending {message} to client: {client}")
            self.send_response(client, message)

    def send_response(self, identity, response):
        self.socket.send_multipart([identity, response.encode()])



class PSUQueue:
    def __init__(self, psu, server):
        self.psu = psu
        self.server = server
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def add_command(self, identity, request):
        self.queue.put((identity, request))

    def worker(self):
        while True:
            identity, request = self.queue.get()
            command = request["command"]
            try:
                response = self.psu.query(command)
            except Exception as e:
                response = f"Error: {e}"
                print(f"Command {command} failed: {e}")

            reply = {
                "id": request.get("id"),
                "address": request["address"],
                "response": response
            }

            print(f"Executed {command} -> {response}")

            self.server.send_response(identity, json.dumps(reply))



if __name__ == "__main__":
    # Start with empty PSU queues dict
    psu_queues = {}  # No instruments connected yet

    # Create server instance
    server = Server(psu_queues)

    # Run the server loop in a background thread
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    print("Server running. Waiting for clients...")

    # Keep main thread alive
    try:
        while True:
            # Optional: periodic tasks, logging, or heartbeat
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("Server shutting down...")