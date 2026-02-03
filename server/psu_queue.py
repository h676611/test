import threading
import queue
import json

class PSUQueue:
    """Manages a queue of SCPI commands for a PSU to ensure sequential processing."""
    
    SET_COMMANDS = ["INST OUT", "VOLT", "CURR", "OUTP:STATe"]

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
                # Send command to PSU
                response = self.psu.query(command)  # your PSU class handles setter vs getter
                
                # If this is a setter, broadcast updated state
                if any(cmd in command for cmd in self.SET_COMMANDS):
                    self.psu.write(command)
                    state = self.psu.get_state()
                    state_reply = {
                        "type": "status_update",
                        "address": request["address"],
                        "status": state
                    }
                    # print(f"Broadcasting state update: {state_reply}")
                    self.server.broadcast(json.dumps(state_reply))

            except Exception as e:
                response = f"Error: {e}"
                print(f"Command {command} failed: {e}")

            # Always send reply to the client that sent the command
            reply = {
                "id": request.get("id"),
                "address": request["address"],
                "response": response
            }
            # print(f"Sending reply to client: {reply}")
            self.server.send_response(identity, json.dumps(reply))
