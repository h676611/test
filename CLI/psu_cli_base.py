from zmq_client import ZMQClient


def run_cli(parser_class, psu_name, inargs=None):
    parser = parser_class()
    args = parser.parse_args(inargs)

    payload = {
        k: v for k, v in vars(args).items()
        if v is not None and v is not False
    }

    request = {
        "name": psu_name,
        "payload": payload
    }

    print(request)

    zmq_client = ZMQClient()
    reply = zmq_client.send_receive(request)
    print(reply)

    return reply
