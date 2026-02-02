import json
import uuid
from PyQt5 import QtWidgets, QtCore

class ControlRow(QtWidgets.QWidget):
    send_request = QtCore.pyqtSignal(dict)

    def __init__(self, instrument, parent=None):
        super().__init__(parent)
        self.instrument = instrument

        layout = QtWidgets.QHBoxLayout(self)

        self.label = QtWidgets.QLabel(instrument)
        layout.addWidget(self.label)

        # Status label
        self.status_label = QtWidgets.QLabel("Idle")
        layout.addWidget(self.status_label)

        # Toggle button
        self.toggle_button = QtWidgets.QPushButton("Connect")
        self.toggle_button.clicked.connect(self.on_toggle)
        layout.addWidget(self.toggle_button)

        # Voltage display and input
        self.voltage_label = QtWidgets.QLabel("Voltage: N/A")
        layout.addWidget(self.voltage_label)

        # Input for setting voltage
        self.voltage_input = QtWidgets.QLineEdit()
        self.voltage_input.setPlaceholderText("Set Voltage")
        layout.addWidget(self.voltage_input)

        # Button to send voltage command
        self.send_voltage_button = QtWidgets.QPushButton("Set Voltage")
        self.send_voltage_button.clicked.connect(self.on_set_voltage)
        layout.addWidget(self.send_voltage_button)

    def send_scpi_command(self, command):
        request_id = str(uuid.uuid4())
        request = {
            "type": "scpi",
            "id": request_id,
            "address": self.instrument,
            "command": command
        }
        self.send_request.emit(request)
        return request_id
    
    def on_set_voltage(self):
        voltage = self.voltage_input.text()
        try:
            voltage_val = float(voltage)
        except ValueError:
            self.status_label.setText("Invalid voltage")
            return

        if not (0.1 <= voltage_val <= 30.0):
            self.status_label.setText("Voltage out of range")
            return

        command = f"VOLT {voltage}"
        self.status_label.setText("Setting Voltage…")
        self.send_scpi_command(command)

    def on_toggle(self):
        self.status_label.setText("Sending…")
        self.send_request.emit({
            "type": "system",  # or "scpi" depending on action
            "action": "connect" if self.toggle_button.text() == "Connect" else "disconnect",
            "address": self.instrument
        })

    @QtCore.pyqtSlot(dict)
    def handle_reply(self, reply):
        if reply.get("address") != self.instrument:
            return

        if reply.get("status") == "error":
            self.handle_error(reply.get("message"))
        elif reply.get("type") == "status_update":
            self.handle_status_update(reply.get("status"))
        else:
            self.status_label.setText(f"Status: {reply.get('status')}")


    def handle_status_update(self, status):
        self.status_label.setText(f"Status: {status.get('connected' if status.get('connected') else 'disconnected')}")
        if status.get('connected'):
            self.toggle_button.setText("Disconnect")
        else:
            self.toggle_button.setText("Connect")

        self.voltage_label.setText(f"Voltage: {status.get('voltage')} V")

    def handle_voltage_update(self, voltage):
        self.voltage_label.setText(f"Voltage: {voltage} V")
    
    def handle_error(self, message):
        self.status_label.setText(f"Error: {message}")
