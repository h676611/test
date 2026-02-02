from PyQt5 import QtCore
import zmq, threading, time

class ZmqClient(QtCore.QObject):
    reply_received = QtCore.pyqtSignal(dict)

    def __init__(self, address="tcp://localhost:5555"):
        super().__init__()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(address)

        # Polling thread for server replies
        self._running = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    @QtCore.pyqtSlot(dict)
    def send(self, request: dict):
        print(f"ZmqClient sending: {request}")
        self.socket.send_json(request)

    def _poll_loop(self):
        while self._running:
            try:
                reply = self.socket.recv_json(flags=zmq.NOBLOCK)
                self.reply_received.emit(reply)
                print(f"ZmqClient received: {reply}")
            except zmq.Again:
                time.sleep(0.01)

    def stop(self):
        self._running = False
        self._poll_thread.join()
