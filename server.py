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

    def start(self):
        print("Server started")
        while True:
            identity, message = self.socket.recv_multipart()
            request = json.loads(message.decode())
            print(f"Received request from {identity}: {request}")
            # Dispatch command to correct PSU queue
            address = request["address"]
            command = request["command"]
            psu_queue = self.psu_queues[address]
            psu_queue.add_command(identity, command)

    def send_response(self, identity, response):
        self.socket.send_multipart([identity, response.encode()])


class PSUQueue:
    def __init__(self, psu, server):
        self.psu = psu
        self.server = server
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def add_command(self, identity, command):
        self.queue.put((identity, command))

    def worker(self):
        while True:
            identity, command = self.queue.get()
            try:
                response = self.psu.query(command)
            except Exception as e:
                response = f"Error: {e}"
            print(f"Executed {command} -> {response}")
            self.server.send_response(identity, response)


if __name__ == "__main__":
    rm = pyvisa.ResourceManager('dummy_psu.yaml@sim')
    psus = {
        "ASRL1::INSTR": rm.open_resource("ASRL1::INSTR"),
        "ASRL2::INSTR": rm.open_resource("ASRL2::INSTR"),
    }

    # Create PSU queues (workers start automatically)
    psu_queues = {addr: PSUQueue(psu, None) for addr, psu in psus.items()}

    # Create server and assign server reference to queues
    server = Server(psu_queues)
    for queue_obj in psu_queues.values():
        queue_obj.server = server

    server.start()
