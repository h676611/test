import argparse

class Parser(argparse.ArgumentParser):
    def __init__(self):
        # Initialize the parent class
        super().__init__(description="CLI Client Parser")
        
        # Add your specific arguments here
        self.add_argument(
            '--scpi',
            nargs=2,
            type=str,
            required=False,
            help='Command to execute'
        )

        self.add_argument(
            '--system',
            '-sys',
            nargs=1,
            type=str,
            help='Send system request'
        )

