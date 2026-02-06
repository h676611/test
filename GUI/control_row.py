import json
import uuid
from PyQt5 import QtWidgets, QtCore
from server.requestKomponents import generateRequest

class ControlRow(QtWidgets.QWidget):
    """A GUI control row for a single instrument, allowing connection management and SCPI command sending."""
    send_request = QtCore.pyqtSignal(dict)

    def __init__(self, instrument, parent=None):
        super().__init__(parent)
        self.instrument = instrument

        self.connected = False
        
        # Main container
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # 1. Create lists to store your widgets so you can access them later
        self.rows = [] 
        
        num_rows = 4 if instrument == "ASRL1::INSTR" else 1

        # connect button
        self.toggle_button = QtWidgets.QPushButton("Start")
        self.toggle_button.clicked.connect(self.on_toggle)
        main_layout.addWidget(self.toggle_button)

        self.state_label = QtWidgets.QLabel("State")
        main_layout.addWidget(self.state_label)


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

            # Output on/off
            row_widgets['on_off_channel_toggle'] = QtWidgets.QCheckBox()
            row_layout.addWidget(row_widgets["on_off_channel_toggle"])

            # Send Button
            send_btn = QtWidgets.QPushButton(f"Send")
            
            # 2. Use lambda with a default variable 'row=i' to capture the current index
            # send_btn.clicked.connect(lambda checked, row=i: self.on_row_submitted(row, row_widgets["on_off_channel_toggle"].isChecked()))
            send_btn.clicked.connect(
                lambda checked, row=i, toggle=row_widgets["on_off_channel_toggle"]:
                    self.on_row_submitted(row, toggle.isChecked())
            )
            row_layout.addWidget(send_btn)

            # Store the dictionary in our list and add layout to screen
            self.rows.append(row_widgets)
            main_layout.addLayout(row_layout)


    def send_scpi_command(self, commands):
        request_id = str(uuid.uuid4())
        request = generateRequest("scpi_request", self.instrument, request_id, commands)
        self.send_request.emit(request)
        return request_id

    def on_toggle(self):

        self.send_request.emit({
            "type": "system_request",
            "payload": ["disconnect" if self.connected else "connect"],
            "address": self.instrument
        })
        if self.connected:
            self.toggle_button.setText("Start")
        else:
            self.toggle_button.setText("Stop")

        print(f"button is: {self.connected}")
        self.connected = not self.connected

    @QtCore.pyqtSlot(dict)
    def handle_reply(self, reply):
        if reply.get("address") != self.instrument:
            return

        print(f'received reply: {reply}')
        
        if reply.get("status") == "error":
            self.handle_error(reply.get("message"))
        elif reply.get("type") == "status_update":
            self.handle_status_update(reply.get("status"))
        # TODO
        # else:
            # self.status_label.setText(f"Status: {reply.get('status')}")


    def handle_status_update(self, status):
        # TODO

        pass

    def handle_voltage_update(self, voltage):
        # TODO
        pass
    
    def handle_error(self, message):
        # TODO
        pass

    # 3. The function that handles the logic
    def on_row_submitted(self, row_index, checked):
        # Access the specific widgets using the row_index
        
        target_row = self.rows[row_index]
        v_val = target_row['voltage_input'].value()
        i_val = target_row['current_input'].value()
        channel = row_index + 1
        # print(f'checked is {checked}')
        request = generateRequest("scpi_request", self.instrument, 1, [f'INST OUT {channel}', f'VOLT {v_val}', f'CURR {i_val}', f'OUTP {1 if checked else 0}'])
        # print(f"Sending {request} to {self.instrument}")
        self.send_request.emit(request)
        