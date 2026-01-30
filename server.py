import pyvisa
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://localhost:5555")
    
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

rm = pyvisa.ResourceManager('dummy_psu.yaml@sim')
dummy_psu = rm.open_resource("ASRL1::INSTR")

while True:
    socks = dict(poller.poll(1000))
    if socket in socks:
        request = socket.recv().decode()
        print(f"Received request: {request}")
        response = dummy_psu.query(request)
        print(f"Responding with: {response}")
        socket.send(response.encode())
