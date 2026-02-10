from CLI_zmq_client import CLI_zmq_client
from Parser import Parser
if __name__=="__main__":
    address = "ASRL1::INSTR"
    client = CLI_zmq_client()
    parser = Parser()
    