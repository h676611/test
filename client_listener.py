import threading

import zmq
from zmq_client import ZmqClient

if __name__ == "__main__":
    client = ZmqClient()
    address = "ASRL1::INSTR"

    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect("tcp://localhost:5556")
    sub.setsockopt_string(zmq.SUBSCRIBE, "") # endre til "ASRL1" om de bare skal få updates på psuen de er på

    client.send_system(address, ["status"], req_id=0)

    def listen():
        while True:
            print("status:", sub.recv_json())

    threading.Thread(target=listen, daemon=True).start()
    input("Press Enter to exit\n")