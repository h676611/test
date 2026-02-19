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

        self.SET_COMMANDS = ["INST OUT", "VOLT", "CURR", "CURR VLIM", "VOLT ILIM", "OUTP"]

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
        command = command.strip(' ')


        

        # if set command, update state
        if any(command.startswith(cmd) for cmd in self.SET_COMMANDS):

            self.resource.write(command)
            logger.debug(f'writing {command}')

            read_response = self.resource.read()
            logger.debug(f'write response: {read_response}')

            try:
                match = re.match(r"(.+)\s+(-?\d+(?:\.\d*)?|-?\.\d+)$", command)
                name = match.group(1)

                value = float(match.group(2))

                if name == "INST OUT": # check channel change
                    self.selected_channel = int(value)
                    return read_response

                self.states[self.selected_channel][name] = value
                

            except Exception as e:
                logger.error(f"exeption {e} for {command}")

        response = self.resource.query(command)
        logger.debug(f'query response: {response}')

        return response

    def get_state(self):
        return self.states
