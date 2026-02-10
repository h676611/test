import sys
import time
import zmq
import random
import json

class ZMQClient:
     def __init__(self, address="tcp://localhost:5555", scpi_address="ASRL1::INSTR"):
         self.context = zmq.Context()
         self.socket = self.context.socket(zmq.DEALER)
         self.socket.connect(address)
         self.scpi_address = scpi_address

     def send_request(self, request):
         self.socket.send_json(request)
         reply = self.socket.recv_json()
         return reply
     
     def set_property(self, prop, value):
         request = {
             "type": "scpi_request",
             "address": "ASRL1::INSTR",
             "id": "1",
             "payload": {
                 "command": f"SET {prop} {value}"
             }
         }
         return self.send_request(request)
     
     def set_channel_current_voltage(self, channel, current, voltage):
         request = {
             "type": "scpi_request",
             "address": "ASRL1::INSTR",
             "id": 1,
             "payload": {
                 "command": f"INST OUT{channel};CURR {current};VOLT {voltage}"
             }
         }
         return self.send_request(request)

import sys, os
sys.path.append(os.getcwd())

import argparse
import pprint

client = ZMQClient()

def common_parser():
    formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=52)
    parser = argparse.ArgumentParser(formatter_class=formatter)

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        default=False,
        help="Enable output"
    )
    parser.add_argument(
        '--mode',
        '-m',
        dest="mode",
        default="pyvisa",
        type=str,
        choices=["pyvisa", "zmq", "dummy"],
        help="Mode for connecting to PSU"
    )
    parser.add_argument(
        '--port',
        '-p',
        dest="port",
        default="9999",
        metavar="XXXX",
        help="Port number to connect to when operating PSU remotely in zmq mode"
    )
    parser.add_argument(
        '--dryrun',
        '-d',
        action='store_true',
        default=False,
        help="dryrun mode. Read inputs, but dont execute program"
    )
    parser.add_argument(
        "--remote",
        "-r",
        dest="remote",
        type=str,
        default=None,
        help="Remote IP of message queue"
    )
    parser.add_argument(
        "--log-level",
        "-ll",
        dest="log_level",
        type=str,
        choices=["INFO", "DEBUG", "ERROR"],
        default="INFO",
        help="Set logger level"
    )
    return parser

def hmp4040_parser(parser):
    parser.set_defaults(port="5555")
    parser.add_argument(
        '--set-channel',
        '-sch',
        dest="set_channel",
        type=int,
        choices=[1,2,3,4],
        help="Select channel"
    )
    parser.add_argument(
        '--set-output-all',
        '-soa',
        dest="set_output_all",
        type=str,
        choices=["True", "False", "true", "false", "0", "1"],
        help="Activate output for all channels"
    )
    parser.add_argument(
        '--address',
        '-a',
        dest="address",
        default="ASRL5::INSTR",
        type=str,
        metavar="address",
        help="Pyvisa device address, when connecting to PSU using 'pyvisa' mode"
    )
    return parser

def make_parser():
    parser = common_parser()
    parser = hmp4040_parser(parser)
    parser = remote_parser(parser)
    parser.descritpion = ("A script enabliong command line controll of a "
                          + "R&S HMP4040 power supply unit")

    return parser





import argparse
import threading
import os
import pprint

def check_dryrun(args):
    if args.dryrun:
        print("Dryrun mode. Would have executed program with the following parameters")
        pprint.pprint(vars(args))
        print("Exiting")
        exit()

def check_path(path, verbose):
    path = str(path)
    if path[-1] != "/":
        path += "/"
    if not os.path.exists(path):
        os.makedirs(path)
        if verbose:
            print("Created folder ", path)
    return path

class KeyboardThread(threading.Thread):
    """A listener class running in a separate thread.
    Once return has been pressed, the class state will signal termination
    of the main program loop.
    """
    def __init__(self, name='keyboard-input-thread'):
        super(KeyboardThread, self).__init__(name=name)
        self.kill = False
        self.start()

    def run(self):
        try:
            input()
            self.kill = True
        except EOFError as e:
            print("error")



def monitor_parser(parser):
    parser.add_argument(
        "--save-output",
        "-sao",
        dest="save_output",
        type=bool,
        default=True,
        help="Save monitor data to file?"
    )
    parser.add_argument(
        "--delay",
        "-dy",
        dest="delay",
        type=float,
        default=1.0,
        help="Delay between measurements"
    )

    return parser



def k2450_parser(parser):
    """Parser for Keithley 2450 PSU"""
    parser.add_argument(
        '--address',
        '-a',
        dest="address",
        default="USB0::0x05E6::0x2450::04424778::INSTR",
        type=str,
        metavar="address",
        help="Pyvisa device address for Keithley 2450"
    )
    parser.set_defaults(port="5556")

    parser.add_argument(
	"--set-autorange",
	"-sa",
	dest="set_autorange",
	action='store_true',
	help="set current autorange"
    )
    parser.add_argument(
	"--set-voltage-range",
	"-svr",
	dest="set_voltage_range",
	type=str,
	help="Set source voltage max range"
    )
	
    return parser

def k2400_parser(parser):
    """Parser for Keithley 2400 PSU"""
    parser.add_argument(
        '--address',
        '-a',
        dest="address",
        default="USB0::0x05E6::0x2400::XXXXXXXX::INSTR",
        type=str,
        metavar="address",
        help="Pyvisa device address for Keithley 2400"
    )
   
    # You can change the default port here if you like:
    parser.set_defaults(port="5556")
    return parser

def k6500_parser(parser):
    parser.set_defaults(port="5557")
    parser.add_argument(
        '--address',
        '-a',
        dest="address",
        default="USB0::0x05E6::0x6500::04543021::INSTR",
        type=str,
        metavar="address",
        help="Pyvisa device address for Keithley 6500"
    )
    parser.add_argument(
        "--get-channel-voltage",
        "-gcv",
        dest="get_channel_voltage",
        type=int,
        help="measure voltage at specified channel"
    )
    return parser

def mm_parser(parser):
    """Multimeter inputs"""
    parser.set_defaults(port="5557")
    parser.add_argument(
        '--get-voltage',
        '-gv',
        dest="get_voltage",
        action='store_true',
        default=argparse.SUPPRESS,
        help="Measure PSU voltage"
    )
    parser.add_argument(
        '--set-channel',
        '-sch',
        dest="set_channel",
        type=int,
        choices=[1,2,3,4,5,6,7,8,9,10],
        help="Select channel"
    )
    parser.add_argument(
        '--get-channel',
        '-gch',
        dest="get_channel",
        action='store_true',
        default=argparse.SUPPRESS,
        help="Get all closed channels on the multimeter"
    )
    return parser

def remote_parser(parser):
    """Common input arguments for PSU remote control scripts."""
    parser.add_argument(
        '--set-output',
        '-so',
        dest="set_output",
        type=str,
        choices=["True", "False", "true", "false", "0", "1"],
        help="Activate output for the active channel"
    )
    parser.add_argument(
        '--set-current',
        '-sc',
        dest="set_current",
        type=float,
        metavar="A",
        help="Set PSU current"
    )
    parser.add_argument(
        '--set-voltage',
        '-sv',
        dest="set_voltage",
        type=float,
        metavar="V",
        help="Set PSU voltage",
    )
    parser.add_argument(
        '--get-voltage',
        '-gv',
        dest="get_voltage",
        action='store_true',
        default=argparse.SUPPRESS,
        help="Measure PSU voltage"
    )
    parser.add_argument(
        '--get-id',
        '-id',
        dest="get_id",
        action='store_true',
        default=argparse.SUPPRESS,
        help="Query instrument ID"
    )
    parser.add_argument(
        '--get-current',
        '-gc',
        dest="get_current",
        action='store_true',
        default=argparse.SUPPRESS,
        help="Measure PSU current"
    )
    parser.add_argument(
        '--get-channel',
        '-gch',
        dest="get_channel",
        action='store_true',
        default=argparse.SUPPRESS,
        help="Get the channel number of the active channel"
    )
    parser.add_argument(
        '--get-display-current',
        '-gdc',
        dest="get_display_current",
        action='store_true',
        default=argparse.SUPPRESS,
        help="Get display current of active channel"
    )
    parser.add_argument(
        '--get-display-voltage',
        '-gdv',
        dest="get_display_voltage",
        action='store_true',
        default=argparse.SUPPRESS,
        help="Get display voltage of active channel"
    )
    parser.add_argument(
        '--set-current-limit',
        '-scl',
        dest="set_current_limit",
        type=float,
        metavar="A",
        help="Set the current limit"
    )
    parser.add_argument(
        '--set-voltage-limit',
        '-svl',
        dest="set_voltage_limit",
        type=float,
        metavar="V",
        help="Set the voltage limit"
    )
    parser.add_argument(
        '--get-current-limit',
        '-gcl',
        dest="get_current_limit",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Get the current limit"
    )
    parser.add_argument(
        '--get-voltage-limit',
        '-gvl',
        dest="get_voltage_limit",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Get the voltage limit"
    )
    parser.add_argument(
        "--get-channel-voltage",
        "-gcv",
        dest="get_channel_voltage",
        type=int,
        help="measure voltage at specified channel"
    )
    parser.add_argument(
        "--get-channel-current",
        "-gcc",
        dest="get_channel_current",
        type=int,
        help="measure current at specified channel"
    )
    parser.add_argument(
        "--get-channel-display-voltage",
        "-gcdv",
        dest="get_channel_display_voltage",
        type=int,
        help="measure display voltage at specified channel"
    )
    parser.add_argument(
        "--get-channel-display-current",
        "-gcdc",
        dest="get_channel_display_current",
        type=int,
        help="measure display current at specified channel"
    )
    parser.add_argument(
        "--set-channel-voltage",
        "-scv",
        dest="set_channel_voltage",
        nargs=2,
        metavar=('CHANNEL', 'VOLTAGE'),
        help="set VOLTAGE at specified CHANNEL"
    )
    parser.add_argument(
        "--set-channel-current",
        "-scc",
        dest="set_channel_current",
        nargs=2,
        metavar=('CHANNEL', 'CURRENT'),
        help="set CURRENT at specified channel CHANNEL"
    )
    parser.add_argument(
        "--set-channel-current-voltage",
        "-sccv",
        dest="set_channel_current_voltage",
        nargs=3,
        metavar=('CHANNEL', 'CURRENT', 'VOLTAGE'),
        help="set CURRENT and VOLTAGE at specified channel CHANNEL"
    )
    return parser

def IV_parser(parser):
    """Argument parser for IV test"""
    parser.add_argument(
        "--tag",
        "-t",
        dest="tag",
        type=str,
        metavar="tag",
        default="",
        help="Name tag for output file"
    )
    parser.add_argument(
        "--path",
        "-pa",
        dest="path",
        metavar="path",
        default="output/",
        help="Path for output file(s)"
    )
    parser.add_argument(
        "--config",
        "-c",
        dest="config",
        type=str,
        default="config/default_IV_conf.json",
        metavar="path_to_config",
        help="Read input parameters from JSON"
    )
    parser.add_argument(
        "--start",
        "-s",
        dest="start",
        type=int,
        default=0,
        metavar="V",
        help="Starting voltage in volts"
    )
    parser.add_argument(
        "--end",
        "-e",
        dest="end",
        type=int,
        default=10,
        metavar="V",
        help="Stopping voltage in volts"
    )
    parser.add_argument(
        "--step",
        "-sp",
        dest="step",
        type=int,
        default=1,
        metavar="V",
        help="Voltage step in volts"
    )
    parser.add_argument(
        "--step-time",
        "-st",
        dest="step_time",
        type=int,
        default=1,
        metavar="S",
        help="Time at each step in seconds"
    )
    parser.add_argument(
        "--limit",
        "-l",
        dest="limit",
        type=float,
        default=1E-4,
        metavar="I",
        help="Current compliance limit in amps"
    )
    parser.add_argument(
        "--show",
        "-sh",
        dest="show",
        action="store_true",
        default=False,
        help="Show results during measurement"
    )
    parser.add_argument(
        "--plot",
        "-pl",
        dest="plot",
        action="store_true",
        default=False,
        help="Plot results after measurement"
    )
    parser.add_argument(
        "--samples",
        "-n",
        dest="samples",
        type=int,
        default=10,
        metavar="N",
        help="Number of current measurements at each voltage"
    )
    parser.add_argument(
        "--hyst",
        "-hy",
        dest="hyst",
        action='store_true',
        default=False,
        help="Enable hysteresis mode"
    )
    parser.add_argument(
        "--hyst-iters",
        "-hi",
        dest="hyst_iters",
        type=int,
        default=5,
        metavar="N",
        help="Number of cycles in hysteresis mode"
    )
    return parser

def VI_parser(parser):
    """Argument parser for VI test"""
    parser.add_argument(
        "--tag",
        "-t",
        dest="tag",
        type=str,
        metavar="tag",
        help="Name tag for output file"
    )
    parser.add_argument(
        "--path",
        "-pa",
        dest="path",
        metavar="path",
        help="Path for output file(s)"
    )
    parser.add_argument(
        "--config",
        "-c",
        dest="config",
        type=str,
        metavar="path_to_config",
        help="Read input parameters from JSON"
    )
    parser.add_argument(
        "--start",
        "-s",
        dest="start",
        type=int,
        metavar="I",
        help="Starting current in amps"
    )
    parser.add_argument(
        "--end",
        "-e",
        dest="end",
        type=int,
        metavar="I",
        help="Stopping current in amps"
    )
    parser.add_argument(
        "--step",
        "-sp",
        dest="step",
        type=int,
        metavar="I",
        help="Current step in amperes"
    )
    parser.add_argument(
        "--step-time",
        "-st",
        dest="step_time",
        type=int,
        metavar="S",
        help="Time at each step in seconds"
    )
    parser.add_argument(
        "--limit",
        "-l",
        dest="limit",
        type=float,
        metavar="V",
        help="Voltage compliance limit in volts"
    )
    parser.add_argument(
        "--show",
        "-sh",
        dest="show",
        action="store_true",
        help="Show results during measurement"
    )
    parser.add_argument(
        "--plot",
        "-pl",
        dest="plot",
        action="store_true",
        default=False,
        help="Plot results after measurement"
    )
    parser.add_argument(
        "--samples",
        "-n",
        dest="samples",
        type=int,
        metavar="N",
        help="Number of voltage measurements at each current value"
    )
    return parser





def main(inargs=None):
    """A script enabling controll of R&S HMP4040 PSU through the command line"""
    parser = make_parser()
    args = parser.parse_args(inargs)
    check_dryrun(args)
    # logger = get_logger("hmp4040_remote", verbose=args.verbose,
    #                     log_level=args.log_level)

    client.send_request({
        "type": "system_request",
        "address": "ASRL1::INSTR",
        "id": 0,
        "payload": {
            "action": "connect"
            }
        })

    for arg in vars(args):
        if arg.startswith("set_") and getattr(args, arg) is not None:
            # logger.debug("Running command: {}".format(arg))
            if arg == "set_channel_current_voltage":
                channel = int(getattr(args,arg)[0])
                current = float(getattr(args,arg)[1])
                voltage = float(getattr(args,arg)[2])
                client.set_channel_current_voltage(channel, current, voltage)

            elif arg != "set_channel_current_voltage" and "set_channel_" in arg:
                channel = int(getattr(args,arg)[0])
                val = float(getattr(args,arg)[1])
                print(client.set_channel_property(channel, arg.split("_")[2], val))
            else:
                client.set_property(arg, getattr(args, arg))

    for arg in vars(args):
        if arg.startswith("get_") and getattr(args, arg) is not None:
            # logger.debug("Running command: {}".format(arg))
            if "get_channel_" in arg:
                print(client.get_channel_property(getattr(args,arg)[0], arg.split("_")[2]))
            else:
                print(client.get_property(arg))

if __name__ == "__main__":
    main()