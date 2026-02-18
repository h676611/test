import argparse

class Parser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(description="HMP4040 PSU CLI Client Parser")

        # --- Connection Management ---
        self.add_argument(
            "--connect",
            action="store_true",
            help="Connects PSU to the server"
        )
        self.add_argument(
            "--disconnect",
            action="store_true",
            help="Disconnects PSU from the server"
        )

        # --- Channel & Output Control ---
        self.add_argument(
            '--set-channel', 
            '-sc',
            type=int,
            help='Sets active channel (INST OUT)'
        )

        self.add_argument(
            '--set-output', '-so',
            choices=['0', '1', 'ON', 'OFF'],
            help='Sets output state for selected channel'
        )
        self.add_argument(
            '--set-output-all',
            choices=['0', '1', 'ON', 'OFF'],
            help='Sets global output state (OUTP:GEN)'
        )

        # --- Voltage & Current Setpoints ---
        self.add_argument(
            '--set-voltage', '-sv',
            type=float,
            help='Set voltage for selected channel'
        )
        self.add_argument(
            '--set-current', '-si',
            type=float,
            help='Set current for selected channel'
        )
        self.add_argument(
            '--set-voltage-limit',
            type=float,
            help='Set voltage limit (V-Limit)'
        )
        self.add_argument(
            '--set-current-limit',
            type=float,
            help='Set current limit (I-Limit)'
        )

        # --- Combined Commands ---
        # Usage: --set-iv 12.5 2.0
        self.add_argument(
            '--set-iv',
            nargs=2,
            metavar=('CURRENT', 'VOLTAGE'),
            type=float,
            help='Simultaneously set Current and Voltage'
        )

# --- Measurements & Queries (Getters) ---

        self.add_argument(
            '--get-id',
            action='store_const',
            const='',
            default=argparse.SUPPRESS,
        )

        self.add_argument(
            '--get-channel',
            '-gc',
            action='store_const',
            const='',
            default=argparse.SUPPRESS,
        )

        self.add_argument(
            '--get-voltage',
            action='store_const',
            const='',
            default=argparse.SUPPRESS,
        )

        self.add_argument(
            '--get-current',
            action='store_const',
            const='',
            default=argparse.SUPPRESS,
        )

        self.add_argument(
            '--get-display-voltage',
            action='store_const',
            const='',
            default=argparse.SUPPRESS,
        )

        self.add_argument(
            '--get-display-current',
            action='store_const',
            const='',
            default=argparse.SUPPRESS,
        )

        self.add_argument(
            '--get-error',
            action='store_const',
            const='',
            default=argparse.SUPPRESS,
        )


        # --- System & Modes ---
        self.add_argument(
            '--set-remote',
            choices=['mixed', 'local', 'remote'],
            help='Set system remote/local state'
        )
        self.add_argument(
            '--set-source',
            help='Set source function'
        )
