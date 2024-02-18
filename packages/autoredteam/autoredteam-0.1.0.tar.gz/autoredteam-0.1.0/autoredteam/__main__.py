"""autoredteam CLI entrypoint"""

import sys
from .engine.cli import main as cli_main


def main():
    cli_main(sys.argv[1:])


if __name__ == "__main__":
    main()
