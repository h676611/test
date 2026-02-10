import sys, os
sys.path.append(os.getcwd())
from Parser import Parser
from CLI_zmq_client import CLI_zmq_client
from server.requestKomponents import generate_request
import zmq

def main(inargs=None):
    # If no inargs are passed (default), parse_args() looks at sys.argv
    parser = Parser()
    args = parser.parse_args(inargs)
    request = generate_request(type="scpi_request", address="ASRL1::INSTR")
    request['request_id'] = 1
    payload = request["payload"]
    print(f"Parsed Arguments: {args}")
    for arg in vars(args):
        # print(f'{str(getattr(args, arg))}')
        temp = getattr(args, arg)
        text = temp[0] + ' ' + temp[1]
        print(text)
        request["payload"].append(text)

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
    print(reply)