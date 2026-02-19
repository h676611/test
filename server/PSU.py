import re
from logger import setup_logger
import pyvisa

logger = setup_logger("PSU")
class PSU:
    """Represents a Power Supply Unit with SCPI command handling."""
    def __init__(self, resource, num_channels=4, name="hmp4040"):
        self.name = name

        self.resource = resource

        self.connected = False
        
        self.address = resource.resource_name

        self.selected_channel = 1

        self.states = {}
        for i in range(num_channels):
            self.states[i + 1] = {
                "VOLT": 0.0,
                "CURR": 0.0,
                "VOLT ILIM": 0.0,
                "CURR VLIM": 0.0,
                "OUTP": 0
            }

    def query(self, command):
        # command = command.strip(' ')
        # logger.debug(f'querying {command} length {len(command)}')
        response = self.resource.query(command)
        # logger.debug(f'query response: {response}')
        return response

    def get_state(self):
        return self.states

    def write(self, command):
        self.resource.write(command)
        # logger.debug(f'writing {command}')

        read_response = self.resource.read()
        # logger.debug(f'write response: {read_response}')
        
        try:
            match = re.match(r"^(.*?)\s*(\d+(?:\.\d+)?)$", command)
            name = match.group(1)

            value = match.group(2)
            
            # logger.debug(f'matched name: {name}, value: {value}')

            if "INST OUT" in command: # check channel change
                self.selected_channel = int(value)
                # logger.debug(f'selected channel changed to {self.selected_channel}')
                return read_response

            self.states[self.selected_channel][name] = value
            # logger.debug(f'state updated: {self.states[self.selected_channel]}')
                

        except Exception as e:
            logger.error(f"exeption {e} for {command}")
            
        # logger.debug(f'fpsu state: {self.get_state()}')
        return read_response