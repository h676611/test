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

    def listen():
        while True:
            print("status:", sub.recv_json())

    for reply in client.send_system(address, ["connect"], req_id=1):
        print(reply)

    print(client.send_scpi(address, "VOLT 5.00", req_id=2))
    print(client.send_scpi(address, "CURR 1.00", req_id=3))

    threading.Thread(target=listen, daemon=True).start()
    input("Press Enter to exit\n")

    # # connect + status
    # req = generateRequest("system_request", address, 1, ["connect", "status"])
    # for reply in client.send_request(req):
    #     print(reply)
    #
    # req_status = generateRequest("system_request", address, 1, ["status"])
    #
    # # set voltage
    # client.socket.send_json({
    #     "type": "scpi_request",
    #     "address": address,
    #     "id": 2,
    #     "payload": {"command": "VOLT 5.00"}
    # })
    # print(client.socket.recv_json())
    # for reply in client.send_request(req_status):
    #     print(reply)
    #
    # # set current
    # client.socket.send_json({
    #     "type": "scpi_request",
    #     "address": address,
    #     "id": 3,
    #     "payload": {"command": "CURR 1.00"}
    # })
    # print(client.socket.recv_json())
    # for reply in client.send_request(req_status):
    #     print(reply)