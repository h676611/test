import sys
import time
import zmq
import random
import json

class Client:
     def __init__(self, address="tcp://localhost:5555"):
         self.context = zmq.Context()
         self.socket = self.context.socket(zmq.DEALER)
         self.socket.connect(address)

     def send_request(self, request):
         self.socket.send_json(request)
         reply = self.socket.recv_json()
         return reply
if __name__ == "__main__":
    client = Client()
    address = "ASRL1::INSTR"
    request = {
        "type": "system_request",
        "address": "ASRL1::INSTR",
        "id": 1,
        "payload": {
            "action": "connect"
            }
        }

    print(f"Sending request: {request}")
    reply = client.send_request(request)
    print(f"Received reply: {reply}")


    request = {
        "type": "scpi_request",
        "address": "ASRL1::INSTR",
        "id": 42,
        "payload": {
            "command": "CURR VLIM 2.0"
            }
        }
    print(f"Sending request: {request}")
    reply = client.send_request(request)
    print(f"Received reply: {reply}")

    request = {
        "type": "scpi_request",
        "address": "ASRL1::INSTR",
        "id": 42,
        "payload": {
            "command": "CURR VLIM?"
            }
        }
    print(f"Sending request: {request}")
    reply = client.send_request(request)
    print(f"Received reply: {reply}")


    request = {
        "type": "system_request",
        "address": "ASRL1::INSTR",
        "id": 2,
        "payload": {
            "action": "disconnect"
            }
        }
    print(f"Sending request: {request}")
    reply = client.send_request(request)
    print(f"Received reply: {reply}")
