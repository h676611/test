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

        self.add_argument(
            '--get-channel',
            action='store_const',
            const='',
            default=argparse.SUPPRESS,
        )


        

        # self.add_argument(
        #     '--set-current',
        #     '-sc',
        #     dest="set_current",
        #     type=float,
        #     metavar="A",
        #     help="Set PSU current",
        #     default=argparse.SUPPRESS,
        # )
        # self.add_argument(
        #     '--set-voltage',
        #     '-sv',
        #     dest="set_voltage",
        #     type=float,
        #     metavar="V",
        #     help="Set PSU voltage",
        #     default=argparse.SUPPRESS,
        # )
