import json
import uuid
from PyQt5 import QtWidgets, QtCore
from logger import setup_logger

logger = setup_logger("Control row")

class ControlRow(QtWidgets.QWidget):
    """A GUI control row for a single instrument, allowing connection management and SCPI command sending."""
    send_request = QtCore.pyqtSignal(dict)

    def __init__(self, instrument, name, parent=None):
        super().__init__(parent)
        self.instrument = instrument

        self.connected = False

        self.name = name
        
        # Main container
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # 1. Create lists to store your widgets so you can access them later
        self.rows = [] 
        
        num_rows = 4 if instrument == "ASRL1::INSTR" else 1


        top_layout = QtWidgets.QHBoxLayout()

        main_layout.addLayout(top_layout)

        self.name_label = QtWidgets.QLabel(self.name)
        top_layout.addWidget(self.name_label)

        # connect button
        self.toggle_button = QtWidgets.QPushButton("Start")
        self.toggle_button.clicked.connect(self.on_toggle)
        top_layout.addWidget(self.toggle_button)


        # Header labels
        header_grid = QtWidgets.QGridLayout()
        main_layout.addLayout(header_grid)

        # Labels for the columns to ensure they align
        header_grid.addWidget(QtWidgets.QLabel("Channel"), 0, 0)
        header_grid.addWidget(QtWidgets.QLabel("Voltage [V]"), 0, 1)
        header_grid.addWidget(QtWidgets.QLabel("Current [A]"), 0, 2)
        header_grid.addWidget(QtWidgets.QLabel("Output"), 0, 3)
        header_grid.addWidget(QtWidgets.QLabel("Send"), 0, 4)

        for i in range(num_rows):
            # Create a dictionary to hold this row's widgets
            row_widgets = {}

            # Label
            label_text = f"{i+1}" if num_rows > 1 else instrument
            row_widgets['label'] = QtWidgets.QLabel(label_text)
            header_grid.addWidget(row_widgets['label'], i*2 + 1, 0)
            
            # Voltage Input
            row_widgets['voltage_input'] = QtWidgets.QDoubleSpinBox()
            row_widgets['voltage_input'].setSuffix(' V')
            row_widgets['voltage_input'].setRange(-100., 100.)
            header_grid.addWidget(row_widgets['voltage_input'], i*2 + 1, 1)

            # Current Input
            row_widgets['current_input'] = QtWidgets.QDoubleSpinBox()
            row_widgets['current_input'].setSuffix(' A')
            row_widgets['current_input'].setRange(-10., 10.)
            header_grid.addWidget(row_widgets['current_input'], i*2 + 1, 2)

            # Output on/off
            row_widgets['on_off_channel_toggle'] = QtWidgets.QCheckBox()
            header_grid.addWidget(row_widgets["on_off_channel_toggle"], i*2 + 1, 3)

            # Send Button
            send_btn = QtWidgets.QPushButton(f"Send")
            
            # 2. Use lambda with a default variable 'row=i' to capture the current index
            send_btn.clicked.connect(
                lambda checked, row=i, toggle=row_widgets["on_off_channel_toggle"]:
                    self.on_row_submitted(row, toggle.isChecked())
            )
            header_grid.addWidget(send_btn, i*2 + 1, 4)

            # Live view for read-only
            live_widgets = {}

            # Channel lable
            live_widgets['label'] = QtWidgets.QLabel("(live)")
            header_grid.addWidget(live_widgets['label'], i*2 + 2, 0)

            # Read-only voltage
            live_widgets['voltage_value'] = QtWidgets.QLabel("- V")
            header_grid.addWidget(live_widgets['voltage_value'], i*2 + 2, 1)

            # Read-only current
            live_widgets['current_value'] = QtWidgets.QLabel("- A")
            header_grid.addWidget(live_widgets['current_value'], i*2 + 2, 2)

            # Read-only output
            live_widgets['output_value'] = QtWidgets.QLabel("-")
            header_grid.addWidget(live_widgets['output_value'], i*2 + 2, 3)

            # Legg til live view
            row_widgets['live'] = live_widgets

            # Store the dictionary in our list
            self.rows.append(row_widgets)


    def on_toggle(self):
        if not self.connected:
            self.start()
        else:
            self.stop()

    def start(self):

        # TODO generate request with function
        payload = {
            'connect': True
        }
        request = {
            'name': self.instrument,
            'payload': payload
        }
        self.send_request.emit(request)
        self.toggle_button.setText("Stop")
        self.connected = True


    def stop(self):

        # TODO generate request with function
        payload = {
            'disconnect': True
        }
        request = {
            'name': self.instrument,
            'payload': payload
        }
        self.send_request.emit(request)
        self.toggle_button.setText("Start")
        self.connected = False

    @QtCore.pyqtSlot(int, dict)
    def handle_reply(self, request_id, reply):
        if reply.get("address") != self.instrument:
            return
        logger.info(f"received reply: {reply}")
        # TODO [KAN-19] handle replies
        

    @QtCore.pyqtSlot(dict)
    def handle_status_update(self, msg):
        if msg.get("address") != self.instrument:
            return
        logger.info(f'received status update: {msg}')

        # TODO
        status = msg.get("status")


        if not isinstance(status, dict): # bare håndter dict status payloads og ignorerer alt annet
            return
        for index, row in enumerate(self.rows): # gå igjennom kanaler
            channel = index + 1
            channel_state = status.get(channel) # read channel state
            if channel_state is None:
                channel_state = status.get(str(channel))
            if not isinstance(channel_state, dict): # skip om kanalen ikke har status
                continue
            live = row.get("live", {})
            if "VOLT" in channel_state and "voltage_value" in live:
                live["voltage_value"].setText(f"{channel_state['VOLT']} V")
            if "CURR" in channel_state and "current_value" in live:
                live["current_value"].setText(f"{channel_state['CURR']} A")
            if "OUTP" in channel_state and "output_value" in live:
                live["output_value"].setText("On" if channel_state["OUTP"] else "Off")

    
    @QtCore.pyqtSlot(dict)
    def handle_error(self, message):
        if message.get("address") != self.instrument:
            return
        logger.error(f"received error: {message}")
        # TODO [KAN-20] handle errors

    # 3. The function that handles the logic
    def on_row_submitted(self, row_index, output_checked):
        # Access the specific widgets using the row_index
        target_row = self.rows[row_index]
        v_val = target_row['voltage_input'].value()
        i_val = target_row['current_input'].value()
        channel = row_index + 1
        


        # TODO [KAN-21] generate request with function
        payload = {
            'set_channel': channel,
            'set_voltage': v_val,
            'set_current': i_val,
            'set_output': 1 if output_checked else 0
        }

        request = {
            "name": self.instrument,
            "payload": payload
        }

        self.send_request.emit(request)
        
