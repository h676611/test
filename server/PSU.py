class PSU:
    """Represents a Power Supply Unit with SCPI command handling."""
    def __init__(self, resource):
        self.resource = resource
        self.voltage = 0.0
        self.current = 0.0
        self.output = False
        self.connected = False
        self.address = resource.resource_name
        self.current_limit = 0.0
        self.voltage_limit = 0.0
        self.SET_COMMANDS = ["INST OUT", "VOLT", "CURR", "CURR VLIM", "VOLT ILIM"]
        self.state = {
            "VOLT": self.voltage,
            "CURR": self.current,
            "CURR VLIM": self.voltage_limit,
            "VOLT ILIM": self.current_limit
        }

    def query(self, command: str) -> str:
        response = self.resource.query(command)

        if any(command.startswith(cmd) for cmd in self.SET_COMMANDS):
            print("set command detected!")
            parts = command.split()
            if parts[-1].isnumeric():
                print(f'number {parts[-1]}')
                self.state[parts[0]] = parts[-1]
                print(f'state: {self.state}')


        print(f"Query PSU with command: {command} response: {response}")
        return response

    def get_state(self):
        return {
            "voltage": self.voltage,
            "current": self.current,
            "output": self.output,
            "connected": self.connected,
            "current limit": self.current_limit,
            "voltage limit": self.voltage_limit
        }
