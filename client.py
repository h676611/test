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
    # request = {
    #     "type": "system",
    #     "action": "connect",
    #     "address": address,
    #     "id": 69
    # }
    # print(f"Sending request: {request}")
    # reply = client.send_request(request)
    # print(f"Received reply: {reply}")


    # request = {
    #     "type": "scpi",
    #     "address": address,
    #     "command": "VOLT 2.0",
    #     "id": 1
    # }
    # print(f"Sending request: {request}")
    # reply = client.send_request(request)
    # print(f"Received reply: {reply}")

    while True:
        query = input("Skriv en kommand: ")
        if query == "connect":
            request = {
            "type": "system",
            "action": "connect",
            "address": address,
            "id": 69
            }
        elif query == "disconnect":
            request = {
            "type": "system",
            "action": "disconnect",
            "address": address,
            "id": 69
            }
        elif query == "setVoltage":
            val = float(input("Value for new volt: "))
            request = {
                "type": "scpi",
                "address": address,
                "command": f"VOLT {val}",
                "id": 1
            }
        print(f"Sending request: {request}")
        reply = client.send_request(request)
        print(f"Received reply: {reply}")
