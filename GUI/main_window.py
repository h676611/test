from PyQt5 import QtWidgets, QtCore
from GUI.zmq_client import ZmqClient
from GUI.control_row import ControlRow

class MainWindow(QtWidgets.QMainWindow):
    """Main application window for PSU control GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSU Control GUI")
        self.setGeometry(100, 100, 600, 400)

        self.psus = ["ASRL1::INSTR", "ASRL2::INSTR"]
        self.control_rows = []

        # ZMQ Client
        self.zmq_client = ZmqClient()
        self.zmq_thread = QtCore.QThread()
        self.zmq_client.moveToThread(self.zmq_thread)
        self.zmq_thread.start()

        # Setup GUI
        self.init_ui()

        # Connect signals
        for row in self.control_rows:
            row.send_request.connect(self.zmq_client.send)
            self.zmq_client.reply_received.connect(row.handle_reply)
            self.zmq_client.status_update_received.connect(row.handle_status_update)
            self.zmq_client.error_received.connect(row.handle_error)

        # Request initial status to register GUI with server
        # for psu in self.psus:
        #     request = generateRequest("system_request", psu,1, ["connect","status"])
        #     self.zmq_client.send(request)


    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        self.label = QtWidgets.QLabel("PSU Control Panel")
        layout.addWidget(self.label)

        for psu in self.psus:
            row = ControlRow(psu)
            layout.addWidget(row)
            self.control_rows.append(row)
