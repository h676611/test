from .zmq_client import ZMQClient
import ordered_argparse
from collections import OrderedDict


def run_cli(parser_class, psu_name, inargs=None):
    parser = parser_class()
    args = parser.parse_args(inargs, namespace=ordered_argparse.OrderedNamespace())

    payload = OrderedDict(
        (k, v) for k, v in args.ordered()
        if v is not None and v is not False
    )

    request = {
        "name": psu_name,
        "payload": payload
    }

    print(request)

    zmq_client = ZMQClient()
    reply = zmq_client.send_receive(request)
    print(reply)

    return reply
