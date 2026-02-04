import sys
import time
import zmq
import random
import json
import threading

class Client:
    def __init__(self, address="tcp://localhost:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(address)

    def send_request(self, request):
        self.socket.send_json(request)
        reply = self.socket.recv_json()
        return reply
    
    def start(self):
        address = "ASRL1::INSTR"
        request = {
            "type": "system_request",
            "address": address,
            "id": 1,
            "payload": {
                "action": "connect"
                }
            }

        print(f"Sending request: {request}")
        reply = self.send_request(request)
        print(f"Received reply: {reply}")


        request = {
            "type": "scpi_request",
            "address": address,
            "id": 42,
            "payload": {
                "command": "CURR 2.0"
                }
            }
        print(f"Sending request: {request}")
        reply = self.send_request(request)
        print(f"Received reply: {reply}")

        request = {
            "type": "scpi_request",
            "address": address,
            "id": 42,
            "payload": {
                "command": "MEAS:CURR?"
                }
            }
        print(f"Sending request: {request}")
        reply = self.send_request(request)
        print(f"Received reply: {reply}")


        request = {
            "type": "system_request",
            "address": address,
            "id": 2,
            "payload": {
                "action": "disconnect"
                }
            }
        print(f"Sending request: {request}")
        reply = self.send_request(request)
        print(f"Received reply: {reply}")


if __name__ == "__main__":
    server = Client()

    client_thread = threading.Thread(target=server.start, daemon=True)
    client_thread.start()

    print("Clinet started...")

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("Client shutting down...")