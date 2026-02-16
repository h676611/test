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
            '--connect',
            action='store_true',
            help='Connect to PSU'
        )
