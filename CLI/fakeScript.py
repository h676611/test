import sys, os
sys.path.append(os.getcwd())
from Parser import Parser
from CLI_zmq_client import CLI_zmq_client

def main(inargs=None):
    # If no inargs are passed (default), parse_args() looks at sys.argv
    parser = Parser()
    args = parser.parse_args(inargs)
    
    print(f"Parsed Arguments: {args.host}")

    # Example of using the parsed args with your client
    client = CLI_zmq_client()
    # client.connect(args.host, args.port) 
    
if __name__ == "__main__":
    # To test manually within the script, you could pass:
    # main(['--command', 'status'])
    main()