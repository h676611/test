import sys, os
sys.path.append(os.getcwd())
from Parser import Parser
from CLI_zmq_client import CLI_zmq_client
from server.requestKomponents import generate_request
import zmq

def main(inargs=None):
    parser = Parser()
    args = parser.parse_args(inargs)
    request = generate_request(type="system_request", address="ASRL1::INSTR")
    request["name"] = "HMP4040" # for testing
    request['request_id'] = 1
    payload = []
    system_calls = ["connect", "disconnect"]
    for arg in vars(args):
        print(arg)
        if arg != " " and arg not in system_calls:
            temp =  getattr(args, arg)
            text = "" 
            for char in temp:
                text += char + ' '
            text = text.removesuffix(' ')
            payload.append(arg + ' ' + text)
        else:
            payload.append(arg)
    request["payload"] = payload
    print(f'request: {request}')
    return request


class ZMQClient:
     def __init__(self, address="tcp://localhost:5555", scpi_address="ASRL1::INSTR"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(address)
        self.scpi_address = scpi_address

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
    while True:
        # This line "blocks" (waits) until a message is received
        reply = zmq_client.socket.recv_string() 
        
        print(f"Received: {reply}")