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

    def write(self, command: str):
        reply = self.resource.write(command)
        print(f"Sent command: {command}, Reply: {reply}")
        # If the command sets voltage/current/output, update internal state
        if command.startswith("VOLT "):
            parts = command.split()
            if parts[1] == "ILIM":
                self.voltage_limit = float(parts[2])
            else:
                self.voltage = float(parts[1])
        elif command.startswith("CURR "):
            parts = command.split()
            if parts[1] == "VLIM":
                self.current_limit = float(parts[2])
            else:
                self.current = float(parts[1])
        elif command.startswith("OUTP"):
            self.output = "ON" in command.upper()
        elif command.startswith("INST OUT"):
            pass  # Handle mode switching if necessary
        return reply

    def query(self, command: str) -> str:
        print(f"Querying PSU with command: {command}")
        response = self.resource.query(command)
        print(f"Received response: {response}")
        # If the command reads a value, update state
        if command.startswith("MEAS:VOLT?"):
            self.voltage = float(response)
        elif command.startswith("MEAS:CURR?"):
            self.current = float(response)
        elif command.startswith("OUTP:STATe?"):
            self.output = response.strip().upper() == "ON"
        return response

    def get_state(self):
        return {
            "voltage": self.voltage,
            "current": self.current,
            "output": self.output,
            "connected": self.connected
        }
