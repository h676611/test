import threading
import queue
import json
from requestKomponents import generate_status_update, generate_reply

class PSUQueue:
    """Manages a queue of SCPI commands for a PSU to ensure sequential processing."""

    def __init__(self, psu, server):
        self.psu = psu
        self.server = server
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.address = psu.address
        self.thread.start()
        
    def add_command(self, identity, request):
        self.queue.put((identity, request))

    def worker(self):
        while True:
            identity, request = self.queue.get()
            commands = request.get("payload", {})
            for command in commands:
                response = self.psu.query(command)
                print(f'command: {command} with response: {response}')
            
            print(self.psu.get_state())
            # reply = {
            #     "request_id": request.get("request_id"),
            #     "address": self.address,
            #     "response": response
            # }
            reply = generate_reply(type="scpi_reply", address=self.address, response=response)
            reply["request_id"] = request.get("request_id")
            self.server.send_response(identity, reply)

    def broadcast_update(self):
        state = self.psu.get_state()
        state_message = generate_status_update(type="status_update", state=state, address=self.address)
        self.server.broadcast(state_message)
