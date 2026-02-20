import sys, os
sys.path.append(os.getcwd())
from .Parser import create_base_parser
import zmq
from .helper import process_payload

def main(inargs=None):
    parser = create_base_parser()
    args = parser.parse_args(inargs)
    request = {
        'name': 'ASRL5::INSTR'
    }
    request['request_id'] = 1
    payload = {
        k: v for k, v in vars(args).items()
        if v is not None and v is not False
    }
    print(f"Raw payload before processing: {payload}")
    payload = process_payload(payload)
    request["payload"] = payload
    print(request)
    return request


class ZMQClient:
     def __init__(self, address="tcp://localhost:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(address)

     def send_request(self, request):
        self.socket.send_json(request)
        reply = self.socket.recv_json()
        return reply

if __name__ == "__main__":
    # To test manually within the script, you could pass:
    # main(['--command', 'status'])
    zmq_client = ZMQClient()
    request = main()
    reply = zmq_client.send_request(request)
    print(reply)