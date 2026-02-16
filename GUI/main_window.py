from PyQt5 import QtWidgets, QtCore
from GUI.GUI_zmq_client import ZmqClient
from GUI.control_row import ControlRow

class MainWindow(QtWidgets.QMainWindow):
    """Main application window for PSU control GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSU Control GUI")
        self.setGeometry(100, 100, 600, 400)

        self.psus = ["ASRL1::INSTR", "ASRL2::INSTR", "ASRL3::INSTR"]
        self.connection_names = ["LV Connection", "HV Connection Setup 1", "HV Connection Setup 2", "DMM Connection"]
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



    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        self.label = QtWidgets.QLabel("PSU Control Panel")
        layout.addWidget(self.label)

        for i, psu in enumerate(self.psus):
            name = self.connection_names[i] if i < len(self.connection_names) else None
            row = ControlRow(instrument=psu, name=name)
            layout.addWidget(row)
            self.control_rows.append(row)
