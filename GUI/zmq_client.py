from PyQt5 import QtCore
import zmq, threading, time

class ZmqClient(QtCore.QObject):
    """A ZeroMQ client integrated with PyQt5 for asynchronous communication with the server."""

    reply_received = QtCore.pyqtSignal(dict)

    def __init__(self, address="tcp://localhost:5555", status_address="tcp://localhost:5556"):
        super().__init__()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(address)
        self.sub_socket = self.context.socket(zmq.SUB) # lage en SUB socket for broadcast status updates
        self.sub_socket.connect(status_address) # koble til server PUB port (default 5556)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "") # subscribe til alle topics

        # Polling thread for server replies
        self._running = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    @QtCore.pyqtSlot(dict)
    def send(self, request: dict):
        print(f"ZmqClient sending: {request}")
        self.socket.send_json(request)

    def _poll_loop(self):
        poller = zmq.Poller() # lag poller for flere sockets
        poller.register(self.socket, zmq.POLLIN) # følg med DEALER
        poller.register(self.sub_socket, zmq.POLLIN) # følg med SUB (broadcast updates)
        while self._running:
            events = dict(poller.poll(100)) # vent 100ms for inputs
            if self.socket in events: # sjekk om socket har inputs
                reply = self.socket.recv_json()  # les input
                self.reply_received.emit(reply) # forward til gui handler
            if self.sub_socket in events: # sjekker broadcast status
                reply = self.sub_socket.recv_json() # les broadcast
                self.reply_received.emit(reply) # forward til gui handler

    def stop(self):
        self._running = False
        self._poll_thread.join()
        # lukker begge sockets når gui lukkes
        self.socket.close()
        self.sub_socket.close()
