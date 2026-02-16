import argparse

class Parser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(description="CLI Client Parser")

        self.add_argument(
            '--set-channel',
            '-sc',
            type=str,
            help='Sets channel to change on PSU'
        )

        self.add_argument(
            '--set-output',
            '-so',
            type=str
        )
        
        self.add_argument(
            "--connect",
            dest="connect",  # Optional: explicitly names the attribute
            action="store_true",
            help="Connects PSU from server",
            required=False,
            default=argparse.SUPPRESS,
        )


        self.add_argument(
            "--disconnect",
            dest="disconnect",  # Optional: explicitly names the attribute
            action="store_true",
            help="Disconnects PSU from server",
            required=False,
            default=argparse.SUPPRESS,
        )
