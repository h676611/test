import threading
import queue
import json
from .requestKomponents import generate_status_update, generate_reply
from logger import setup_logger

logger = setup_logger("PSUqueue")

class PSUQueue:
    """Manages a queue of SCPI commands for a PSU to ensure sequential processing."""

    def __init__(self, psu, server):
        self.psu = psu
        self.server = server
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.address = psu.address
        self.SET_COMMANDS = ["INST OUT", "VOLT", "CURR", "CURR VLIM", "VOLT ILIM", "OUTP"]
        self.thread.start()
        
    def add_command(self, identity, request):
        self.queue.put((identity, request))

    def worker(self):
        while True:
            identity, request = self.queue.get()
            commands = request.get("payload", {})
            for command in commands:
                    
                response = self.psu.query(command)
                logger.info(f"Querying command: {command}")
                logger.info(f"Response: {response}")
                if any(command.startswith(cmd) for cmd in self.SET_COMMANDS):
                    self.broadcast_update()
            
            reply = generate_reply(type="scpi_reply", address=self.address, response=response)
            reply["request_id"] = request.get("request_id")
            self.server.send_response(identity, reply)

    def broadcast_update(self):
        state = self.psu.get_state()
        state_message = generate_status_update(state=state, address=self.address)
        self.server.broadcast(state_message)
