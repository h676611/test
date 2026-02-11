import re
from logger import setup_logger

logger = setup_logger("PSU")
class PSU:
    """Represents a Power Supply Unit with SCPI command handling."""
    def __init__(self, resource):
        self.resource = resource
        self.voltage = 0.0
        self.current = 0.0
        self.connected = False
        self.address = resource.resource_name
        self.current_limit = 0.0
        self.voltage_limit = 0.0
        self.selected_channel = 1
        self.SET_COMMANDS = ["INST OUT", "VOLT", "CURR", "CURR VLIM", "VOLT ILIM", "OUTP"]
        self.state = {
            "VOLT": self.voltage,
            "CURR": self.current,
            "CURR VLIM": self.voltage_limit,
            "VOLT ILIM": self.current_limit
        }
        self.states = {}
        self.states[1] = self.state

    def query(self, command: str) -> str:
        response = self.resource.query(command)
        logger.info(f"Querying PSU with command: {command}")
        logger.info(f"Response: {response}")

        if any(command.startswith(cmd) for cmd in self.SET_COMMANDS):
            try:
                match = re.match(r"(.+)\s+(-?\d+(?:\.\d*)?|-?\.\d+)$", command)
                name = match.group(1)

                value = float(match.group(2))

                if name == "INST OUT": # check channel change and create new state for channel
                    temp_state = {
                    }
                    self.selected_channel = value
                    self.states[int(value)] = temp_state
                    return response

                self.states[self.selected_channel][name] = value
                

            except Exception as e:
                logger.error(f"exeption {e} for {command}")

        return response

    def get_state(self):
        return self.states
