import zmq

class ZmqClient:
    def __init__(self, address="tcp://localhost:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(address)

    def send(self, msg):
        self.socket.send_json(msg)

    def recv(self):
        return self.socket.recv_json()

    def send_system(self, address, actions, req_id=0):
        self.send({
            "type": "system_request",
            "address": address,
            "id": req_id,
            "payload": actions
        })
        # one reply per action
        return [self.recv() for _ in actions]

    def send_scpi(self, address, command, req_id=0):
        self.send({
            "type": "scpi_request",
            "address": address,
            "id": req_id,
            "payload": command
        })
        return self.recv()