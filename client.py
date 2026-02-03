import sys
import time
import zmq
import random
import json
from helper.requestKomponents import generateRequest

class Client:
     def __init__(self, address="tcp://localhost:5555"):
         self.context = zmq.Context()
         self.socket = self.context.socket(zmq.DEALER)
         self.socket.connect(address)

     def send_request(self, request):
         self.socket.send_json(request)
         reply = []
         reply.append(self.socket.recv_json())
         reply.append(self.socket.recv_json())
         return reply
if __name__ == "__main__":
    client = Client()
    address = "ASRL1::INSTR"
    request = generateRequest("system_request","ASRL1::INSTR",1,["connect","status"])

    print(f"Sending request: {request}")
    replyes = client.send_request(request)
    for reply in replyes:
        print(f"Received reply: {reply}")
