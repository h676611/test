import queue
import threading
import json

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
            reply = {
                "id": request.get("id"),
                "address": request["address"],
                "response": response
            }
            self.server.send_response(identity, json.dumps(reply))
