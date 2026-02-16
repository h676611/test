import json
import uuid
from PyQt5 import QtWidgets, QtCore
from server.requestKomponents import generate_request
from logger import setup_logger

logger = setup_logger("Control row")

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
            send_btn.clicked.connect(
                lambda checked, row=i, toggle=row_widgets["on_off_channel_toggle"]:
                    self.on_row_submitted(row, toggle.isChecked())
            )
            row_layout.addWidget(send_btn)

            # Store the dictionary in our list and add layout to screen
            self.rows.append(row_widgets)
            main_layout.addLayout(row_layout)


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
        # TODO handle replies
        

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
            if "VOLT" in channel_state:
                row["voltage_input"].setValue(channel_state["VOLT"]) # update gui volt verdi (burde vi lage ny row sånn at verdien alltid står til og med om man begynner å endre på verdiene uten å sende de?)
            if "CURR" in channel_state:
                row["current_input"].setValue(channel_state["CURR"]) # update gui curr verdi
            if "OUTP" in channel_state:
                row["on_off_channel_toggle"].setChecked(bool(channel_state["OUTP"])) # sync sånn at checkboxen viser riktig

    def handle_voltage_update(self, voltage):
        # TODO
        pass
    
    @QtCore.pyqtSlot(dict)
    def handle_error(self, message):
        if message.get("address") != self.instrument:
            return
        logger.error(f"received error: {message}")
        # TODO handle errors

    # 3. The function that handles the logic
    def on_row_submitted(self, row_index, output_checked):
        # Access the specific widgets using the row_index
        target_row = self.rows[row_index]
        v_val = target_row['voltage_input'].value()
        i_val = target_row['current_input'].value()
        channel = row_index + 1
        


        # TODO generate request with function
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
        
