from PyQt5 import QtWidgets, QtCore

class ControlRow(QtWidgets.QWidget):
    send_request = QtCore.pyqtSignal(dict)

    def __init__(self, instrument, parent=None):
        super().__init__(parent)
        self.instrument = instrument

        layout = QtWidgets.QHBoxLayout(self)

        self.label = QtWidgets.QLabel(instrument)
        layout.addWidget(self.label)

        self.status_label = QtWidgets.QLabel("Idle")
        layout.addWidget(self.status_label)

        self.toggle_button = QtWidgets.QPushButton("Start")
        self.toggle_button.clicked.connect(self.on_toggle)
        layout.addWidget(self.toggle_button)

    def on_toggle(self):
        self.status_label.setText("Sending…")
        self.send_request.emit({
            "type": "system",  # or "scpi" depending on action
            "action": "connect" if self.toggle_button.text() == "Start" else "disconnect",
            "address": self.instrument
        })

    @QtCore.pyqtSlot(dict)
    def handle_reply(self, reply):
        if reply.get("address") != self.instrument:
            return

        if reply.get("status") == "error":
            self.status_label.setText(f"Error: {reply.get('message')}")
        elif reply.get("type") == "status_update":
            self.status_label.setText(f"Status: {reply.get('status')}")
            self.toggle_button.setText("Stop" if reply.get("status") == "connected" else "Start")
        else:
            self.status_label.setText(f"Status: {reply.get('status')}")
