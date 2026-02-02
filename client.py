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
         reply = self.socket.recv()
         return reply
if __name__ == "__main__":
    client = Client()
    address = "ASRL1::INSTR"
    request = {
        "type": "system",
        "action": "connect",
        "address": address,
        "id": 69
    }
    print(f"Sending request: {request}")
    reply = client.send_request(request)
    print(f"Received reply: {reply}")


    request = {
        "type": "scpi",
        "address": address,
        "command": "INST OUT 1",
        "id": 1
    }
    print(f"Sending request: {request}")
    reply = client.send_request(request)
    print(f"Received reply: {reply}")


    request = {
        "type": "scpi",
        "address": address,
        "command": "INST:NSEL?",
        "id": 2
    }
    print(f"Sending request: {request}")
    reply = client.send_request(request)
    print(f"Received reply: {reply}")