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
    addresses = ["ASRL1::INSTR", "ASRL2::INSTR"]
    commands = ["?IDN", "PING", "MEASURE:VOLTAGE?", "MEASURE:CURRENT?"]

    for _ in range(10):
        address = random.choice(addresses)
        command = random.choice(commands)
        request = {
            "address": address,
            "command": command
        }
        print(f"Sending request: {request}")
        reply = client.send_request(request)
        print(f"Received reply: {reply}")
        time.sleep(1)