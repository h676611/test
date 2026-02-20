from .Parser import K2400_Parser
from .psu_cli_base import run_cli


if __name__ == "__main__":
    run_cli(K2400_Parser, "k2400")
