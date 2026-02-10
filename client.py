import threading
import zmq
import random
import json
from server.requestKomponents import generateRequest
from zmq_client import ZmqClient

if __name__ == "__main__":
    client = ZmqClient()
    address = "ASRL1::INSTR"

    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect("tcp://localhost:5556")
    sub.setsockopt_string(zmq.SUBSCRIBE, "")  # endre til "ASRL1" om de bare skal få updates på psuen de er på

    def listen():
        while True:
            print("status:", sub.recv_json())

    threading.Thread(target=listen, daemon=True).start()

    for reply in client.send_system(address, ["connect"], req_id=1):
        print(reply)

    print(client.send_scpi(
        address,
        ["INST OUT 1", "VOLT 6.00", "CURR 2.00", "OUTP 1"],
        req_id=2,
    ))

    input("Press Enter to exit\n")
