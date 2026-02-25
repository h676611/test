import re
from logger import setup_logger
import pyvisa
from .Translate import get_dic_for_PSU

logger = setup_logger("PSU")
class PSU:
    """Represents a Power Supply Unit with SCPI command handling."""
    def __init__(self, resource, num_channels=4, name="hmp4040"):
        self.name = name
        self.num_channels = num_channels
        if self.name != "hmp4040":
            self.num_channels = 1

        self.resource = resource

        self.connected = False
        
        self.address = resource.resource_name

        self.selected_channel = 1

        self.states = {}
        for i in range(self.num_channels):
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

            # Map SCPI command back to the correct state key via the translate dict
            COMMAND_TO_STATE = {
                "set_voltage": "VOLT",
                "set_current": "CURR",
                "set_current_limit": "VOLT ILIM",
                "set_voltage_limit": "CURR VLIM",
                "set_output": "OUTP",
            }

            cmd_prefix = name.strip()
            numeric_value = float(value) if '.' in value else int(value)
            dic = get_dic_for_PSU(self.name)

            for cmd_name, scpi_template in dic.items():
                if not isinstance(scpi_template, str):
                    continue
                template_base = scpi_template.replace("{}", "").strip().rstrip(";")
                if cmd_prefix.upper() == template_base.upper():
                    state_key = COMMAND_TO_STATE.get(cmd_name)
                    if state_key and state_key in self.states[self.selected_channel]:
                        self.states[self.selected_channel][state_key] = numeric_value
                    break
                

        except Exception as e:
            logger.error(f"exception {e} for {command}")
            
            
        logger.debug(f'PSU state: {self.get_state()}')
        return read_response