import zmq

from zmq_client import ZmqClient
import json

if __name__ == "__main__":
    client = ZmqClient()
    address = "ASRL1::INSTR"

    client.send_system(address, ["status"], req_id=0)

    print("listening...")
    while True:
        msg = client.recv()
        print("raw:", msg)
        if isinstance(msg, str):
            try:
                print("decoded:", json.loads(msg))
            except Exception:
                pass