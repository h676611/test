import zmq

class CLI_zmq_client():
    def __init__(self, address="tcp://localhost:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)
        self._next_id = 0
        self._pending = set()
        
        
    def send_and_recive(self, request: dict):
        request_id = self._next_id
        self._next_id += 1
        request["request_id"] = request_id
        self._pending.add(request_id)
        print(f'sending request: {request} with request_id: {request_id}')
        reply = self.socket.send_json(request)
        print(f'recived reply: {reply} with reply_id: {reply.id}')
        return reply