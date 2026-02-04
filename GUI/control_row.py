import json
import uuid
from PyQt5 import QtWidgets, QtCore
from server.requestKomponents import generateRequest

class ControlRow(QtWidgets.QWidget):
    """A GUI control row for a single instrument, allowing connection management and SCPI command sending."""

    send_request = QtCore.pyqtSignal(dict)

    # def __init__(self, instrument, parent=None):
        # super().__init__(parent)
        # self.instrument = instrument
        # i = 1
        # if instrument == "ASRL1::INSTR":
        #     i = 4
        # for i in range(0,i):

        #     layout = QtWidgets.QHBoxLayout(self)

        #     self.label = QtWidgets.QLabel(instrument)
        #     layout.addWidget(self.label)

        #     # Status label
        #     self.status_label = QtWidgets.QLabel("Idle")
        #     layout.addWidget(self.status_label)

        #     # Toggle button
        #     self.toggle_button = QtWidgets.QPushButton("Connect")
        #     self.toggle_button.clicked.connect(self.on_toggle)
        #     layout.addWidget(self.toggle_button)

        #     # Voltage display
        #     self.voltage_label = QtWidgets.QLabel("Voltage: ")
        #     layout.addWidget(self.voltage_label)

        #     # Input for setting voltage
        #     self.voltage_input = QtWidgets.QDoubleSpinBox()
        #     self.voltage_input.setRange(-100., 100.)
        #     self.voltage_input.setValue(-10.)
        #     layout.addWidget(self.voltage_input)

        #     #Current display
        #     self.current_label = QtWidgets.QLabel("Current: ")
        #     layout.addWidget(self.current_label)

        #     #input for current
        #     self.current_input = QtWidgets.QDoubleSpinBox()
        #     self.current_input.setRange(-10., 10.)
        #     self.current_input.setValue(5.55)
        #     layout.addWidget(self.current_input)

        #     # Button to send voltage and current values
        #     self.send_voltage_button = QtWidgets.QPushButton("on")
        #     self.send_voltage_button.clicked.connect(self.on_set_voltage)
        #     layout.addWidget(self.send_voltage_button)

    from PyQt5 import QtWidgets

def __init__(self, instrument, parent=None):
    super().__init__(parent)
    self.instrument = instrument
    
    # Main container
    main_layout = QtWidgets.QVBoxLayout(self)
    
    # 1. Create lists to store your widgets so you can access them later
    self.rows = [] 
    
    num_rows = 4 if instrument == "ASRL1::INSTR" else 1

    for i in range(num_rows):
        row_layout = QtWidgets.QHBoxLayout()
        
        # Create a dictionary to hold this row's widgets
        row_widgets = {}

        # Label
        label_text = f"{instrument} - Ch {i+1}" if num_rows > 1 else instrument
        row_widgets['label'] = QtWidgets.QLabel(label_text)
        row_layout.addWidget(row_widgets['label'])

        # Voltage Input
        row_widgets['voltage_input'] = QtWidgets.QDoubleSpinBox()
        row_widgets['voltage_input'].setRange(-100., 100.)
        row_layout.addWidget(row_widgets['voltage_input'])

        # Current Input
        row_widgets['current_input'] = QtWidgets.QDoubleSpinBox()
        row_widgets['current_input'].setRange(-10., 10.)
        row_layout.addWidget(row_widgets['current_input'])

        # Send Button
        send_btn = QtWidgets.QPushButton(f"Set Row {i+1}")
        
        # 2. Use lambda with a default variable 'row=i' to capture the current index
        send_btn.clicked.connect(lambda checked, row=i: self.on_row_submitted(row))
        
        row_layout.addWidget(send_btn)

        # Store the dictionary in our list and add layout to screen
        self.rows.append(row_widgets)
        main_layout.addLayout(row_layout)

# 3. The function that handles the logic
def on_row_submitted(self, row_index):
    # Access the specific widgets using the row_index
    target_row = self.rows[row_index]
    v_val = target_row['voltage_input'].value()
    i_val = target_row['current_input'].value()
    
    print(f"Sending to {self.instrument} [Row {row_index}]: Voltage={v_val}, Current={i_val}")
    # Now you can call your instrument communication logic here

    def send_scpi_command(self, commands):
        request_id = str(uuid.uuid4())
        request = generateRequest("scpi_request", self.instrument, request_id, commands)
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