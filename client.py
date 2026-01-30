import sys
import time
import zmq
import random

class Client:
     def __init__(self, address="tcp://localhost:5555", name="Client"):
         self.context = zmq.Context()
         self.socket = self.context.socket(zmq.REQ)
         self.socket.connect(address)
         self.name = name

     def send_request(self, request):
         self.socket.send(request.encode())
         reply = self.socket.recv()
         return reply

if __name__ == "__main__":
     client = Client(name=sys.argv[1] if len(sys.argv) > 1 else "Client")
     while True:
         random_number = random.random() * 10
         request = f"!FREQ {random_number:.2f}"
        #  request = "!FREQ 2.0"
         print(f"{client.name} sending request: {request}")
         reply = client.send_request(request).decode()
         print(f"Received reply: {reply}")
         time.sleep(1)

         request = "?FREQ"
         print(f"{client.name} sending request: {request}")
         reply = client.send_request(request).decode()
         print(f"Received reply: {reply}")
         time.sleep(1)
