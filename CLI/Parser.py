import argparse

class Parser(argparse.ArgumentParser):
    def __init__(self):
        # Initialize the parent class
        super().__init__(description="CLI Client Parser")
        
        # Add your specific arguments here
        self.add_argument('--host', type=str, default='127.0.0.1', help='Server IP')
        self.add_argument('--port', type=int, default=5555, help='Server Port')
        self.add_argument('--command', type=str, required=True, help='Command to execute')