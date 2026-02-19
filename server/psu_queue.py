import threading
import queue
from logger import setup_logger
from .Translate import get_dic_for_PSU

logger = setup_logger("PSUqueue")

class PSUQueue:
    """Manages a queue of SCPI commands for a PSU to ensure sequential processing."""

    def __init__(self, psu, server):
        self.psu = psu
        self.server = server
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.address = psu.address

        self.name = psu.name
        self.dic = get_dic_for_PSU(self.name)

        self.thread.start()
        
    def add_command(self, identity, payload):
        self.queue.put((identity, payload))

    def worker(self):
        while True:
            identity, payload = self.queue.get()
            last_response = None
            reply_payload = {

            }
            if any(key.startswith("get") for key in payload): #If it is a get command we query the psu
                    for command, args in payload.items():
                        scpi_cmd = self.cli_to_scpi(command, args)

                        logger.info(f"Querying command: {scpi_cmd}")
                        last_response = self.psu.query(scpi_cmd)

                        logger.info(f"Response: {last_response}")

                        reply_payload[command] = last_response
            else: # if it is a set command we just send the command to the psu and then query the state of the psu
                for command, args in payload.items():
                    scpi_cmd = self.cli_to_scpi(command, args)

                    logger.info(f"Writing command: {scpi_cmd}")
                    last_response = self.psu.write(scpi_cmd)

                    logger.info(f"Response: {last_response}")

                    reply_payload[command] = last_response


            if any(key.startswith("set") for key in payload):
                self.broadcast_update()

            reply = {
                "address": self.address,
                "payload": reply_payload
            }

            self.server.send_response(identity, reply)


    def broadcast_update(self):
        state = self.psu.get_state()
        state_message = {
            "type": "status_update",
            "status": state,
            "address": self.address
        }
        self.server.broadcast(state_message)

    def cli_to_scpi(self, command, args):
        
        base_scpi = self.dic.get(command)

        if not base_scpi:
            raise ValueError(f"Unknown CLI command: {command}")

        if isinstance(args, list):
            return base_scpi.format(channel=args[0], voltage=args[1])

        elif isinstance(args, str) or isinstance(args, int) or isinstance(args, float):
            if str(args) == '':
                return base_scpi
            return base_scpi + str(args)

        elif isinstance(args, bool):
            return base_scpi

        else:
            raise ValueError(f"Unsupported argument type for {command}")
