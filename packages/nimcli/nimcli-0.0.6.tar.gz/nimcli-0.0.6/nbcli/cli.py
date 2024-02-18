# The MIT License (MIT)
# Copyright © 2024 Nimble Labs Ltd

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import sys
import shtab
import argparse
import nbcli as nimble
from nbcli import *
from typing import List, Optional

# Create a console instance for CLI display.
console = nimble.__console__

ALIAS_TO_COMMAND = {
    "subnets": "subnets",
    "s": "subnets",
    "wallet": "wallet",
    "stake": "stake",
    "wallets": "wallet",
    "w": "wallet",
    "st": "stake",
}
COMMANDS = {
    "wallet": {
        "name": "wallet",
        "aliases": ["w", "wallets"],
        "help": "Commands for managing and viewing wallets.",
        "commands": {
            "list": ListCommand,
            "overview": OverviewCommand,
            "transfer": TransferCommand,
            "create": WalletCreateCommand,
            "new_hotkey": NewHotkeyCommand,
            "new_coldkey": NewColdkeyCommand,
        },
    },
    "subnets": {
        "name": "subnets",
        "aliases": ["s", "subnet"],
        "help": "Commands for managing and viewing subnetworks.",
        "commands": {
            "register": RegisterCommand,
        },
    },
    "stake": {
        "name": "stake",
        "aliases": ["st", "stakes"],
        "help": "Commands for staking and removing stake from hotkey accounts.",
        "commands": {"show": StakeShow, "add": StakeCommand, "remove": UnStakeCommand},
    },
}


class CLIErrorParser(argparse.ArgumentParser):
    """
    Custom ArgumentParser for better error messages.
    """

    def error(self, message):
        """
        This method is called when an error occurs. It prints a custom error message.
        """
        sys.stderr.write(f"Error: {message}\n")
        self.print_help()
        sys.exit(2)


class cli:
    """
    Implementation of the Command Line Interface (CLI) class for the nimble protocol.
    This class handles operations like key management (hotkey and coldkey) and token transfer.
    """

    def __init__(
        self,
        config: Optional["nimble.config"] = None,
        args: Optional[List[str]] = None,
    ):
        """
        Initializes a nimble.CLI object.

        Args:
            config (nimble.config, optional): The configuration settings for the CLI.
            args (List[str], optional): List of command line arguments.
        """
        # Turns on console for cli.
        nimble.turn_console_on()

        # If no config is provided, create a new one from args.
        if config == None:
            config = cli.create_config(args)

        self.config = config
        if self.config.command in ALIAS_TO_COMMAND:
            self.config.command = ALIAS_TO_COMMAND[self.config.command]
        else:
            console.print(
                f":cross_mark:[red]Unknown command: {self.config.command}[/red]"
            )
            sys.exit()

        # Check if the config is valid.
        cli.check_config(self.config)

        # If no_version_checking is not set or set as False in the config, version checking is done.
        if not self.config.get("no_version_checking", d=True):
            try:
                nimble.utils.version_checking()
            except:
                # If version checking fails, inform user with an exception.
                raise RuntimeError(
                    "To avoid internet-based version checking, pass --no_version_checking while running the CLI."
                )

    @staticmethod
    def __create_parser__() -> "argparse.ArgumentParser":
        """
        Creates the argument parser for the nimble CLI.

        Returns:
            argparse.ArgumentParser: An argument parser object for nimble CLI.
        """
        # Define the basic argument parser.
        parser = CLIErrorParser(
            description=f"nimble cli v{nimble.__version__}",
            usage="nimcli <command> <command args>",
            add_help=True,
        )
        # Add shtab completion
        parser.add_argument(
            "--print-completion",
            choices=shtab.SUPPORTED_SHELLS,
            help="Print shell tab completion script",
        )
        # Add arguments for each sub-command.
        cmd_parsers = parser.add_subparsers(dest="command")
        # Add argument parsers for all available commands.
        for command in COMMANDS.values():
            if isinstance(command, dict):
                subcmd_parser = cmd_parsers.add_parser(
                    name=command["name"],
                    aliases=command["aliases"],
                    help=command["help"],
                )
                subparser = subcmd_parser.add_subparsers(
                    help=command["help"], dest="subcommand", required=True
                )

                for subcommand in command["commands"].values():
                    subcommand.add_args(subparser)
            else:
                command.add_args(cmd_parsers)

        return parser

    @staticmethod
    def create_config(args: List[str]) -> "nimble.config":
        """
        From the argument parser, add config to nimble.executor and local config

        Args:
            args (List[str]): List of command line arguments.

        Returns:
            nimble.config: The configuration object for nimble CLI.
        """
        parser = cli.__create_parser__()

        # If no arguments are passed, print help text and exit the program.
        if len(args) == 0:
            parser.print_help()
            sys.exit()

        return nimble.config(parser, args=args)

    @staticmethod
    def check_config(config: "nimble.config"):
        """
        Checks if the essential configuration exists under different command

        Args:
            config (nimble.config): The configuration settings for the CLI.
        """
        # Check if command exists, if so, run the corresponding check_config.
        # If command doesn't exist, inform user and exit the program.
        if config.command in COMMANDS:
            command = config.command
            command_data = COMMANDS[command]

            if isinstance(command_data, dict):
                if config["subcommand"] != None:
                    command_data["commands"][config["subcommand"]].check_config(config)
                else:
                    console.print(
                        f":cross_mark:[red]Missing subcommand for: {config.command}[/red]"
                    )
                    sys.exit(1)
            else:
                command_data.check_config(config)
        else:
            console.print(f":cross_mark:[red]Unknown command: {config.command}[/red]")
            sys.exit(1)

    def run(self):
        """
        Executes the command from the configuration.
        """
        # Check for print-completion argument
        if self.config.print_completion:
            shell = self.config.print_completion
            print(shtab.complete(parser, shell))
            return

        # Check if command exists, if so, run the corresponding method.
        # If command doesn't exist, inform user and exit the program.
        command = self.config.command
        if command in COMMANDS:
            command_data = COMMANDS[command]

            if isinstance(command_data, dict):
                command_data["commands"][self.config["subcommand"]].run(self)
            else:
                command_data.run(self)
        else:
            console.print(
                f":cross_mark:[red]Unknown command: {self.config.command}[/red]"
            )
            sys.exit()
