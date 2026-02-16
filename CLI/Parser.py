import argparse

class Parser(argparse.ArgumentParser):
    def __init__(self):
        # Initialize the parent class
        super().__init__(description="CLI Client Parser")
        

        self.add_argument(
            '--set-channel',
            '-sc',
            nargs=1,
            type=str,
            required=False,
            default=argparse.SUPPRESS,
            help='Sets channel to change on PSU'
        )

        self.add_argument(
            '--set-output',
            '-so',
            nargs=1,
            type=str,
            required=False,
            default=argparse.SUPPRESS
        )

        self.add_argument(
            "--set-channel-voltage",
            "-scv",
            dest="set_channel_voltage",
            nargs=2,
            metavar=('CHANNEL', 'VOLTAGE'),
            help="set VOLTAGE at specified CHANNEL",
            default=argparse.SUPPRESS,
        )
        
        self.add_argument(
            "--connect",
            dest="connect",  # Optional: explicitly names the attribute
            action="store_const",
            const="connect",
            help="Connects PSU from server",
            required=False,
            default=argparse.SUPPRESS,
        )
        self.add_argument(
            "--disconnect",
            dest="disconnect",  # Optional: explicitly names the attribute
            action="store_const",
            const="disconnect",
            help="Disconnects PSU from server",
            required=False,
            default=argparse.SUPPRESS,
        )

