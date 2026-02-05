import threading
import queue
import json

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
                
            reply = {
                "id": request.get("id"),
                "address": self.address,
                "response": response
            }
            self.server.send_response(identity, reply)

    def broadcast_update(self):
        state = self.psu.get_state()
        state_message = {
            "type": "status_update",
            "address": self.address,
            "status": state
        }
        self.server.broadcast(state_message)

            # try:
            #     # Send command to PSU
                
            #     # If this is a setter, broadcast updated state
            #     if any(cmd in command for cmd in self.SET_COMMANDS):
            #         response = self.psu.write(command)
            #         # state = self.psu.get_state()
            #         # state_reply = {
            #         #     "type": "status_update",
            #         #     "address": self.address,
            #         #     "status": state
            #         # }
            #     else :
            #         response = self.psu.query(command)  # your PSU class handles setter vs getter

            #         # self.server.broadcast(json.dumps(state_reply))

            # except Exception as e:
            #     response = f"Error: {e}"
            #     print(f"Command {command} failed: {e}")

            # # Always send reply to the client that sent the command
            # reply = {
            #     "id": request.get("id"),
            #     "address": self.address,
            #     "response": response
            # }
            # self.server.send_response(identity, json.dumps(reply))
