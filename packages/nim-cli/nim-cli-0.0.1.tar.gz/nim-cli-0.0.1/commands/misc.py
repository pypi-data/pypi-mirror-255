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

import os
import argparse
import nimble
from typing import List
from rich.prompt import Prompt

console = nimble.__console__


class UpdateCommand:
    """
    Executes the 'update' command to update the local nimble package. This command performs a series of operations to ensure that the user's local nimble installation is updated to the latest version from the master branch of its GitHub repository. It primarily involves pulling the latest changes from the repository and reinstalling the package.

    Usage:
    Upon invocation, the command first checks the user's configuration for the 'no_predict' setting. If 'no_predict' is set to True, or if the user explicitly confirms with 'Y' when asked, the command proceeds to update the local nimble package. It changes the current directory to the nimble package directory, checks out the master branch of the nimble repository, pulls the latest changes, and then reinstalls the package using pip.

    The command structure is as follows:
    1. Change directory to the nimble package directory.
    2. Check out the master branch of the nimble GitHub repository.
    3. Pull the latest changes with the '--ff-only' option to ensure a fast-forward update.
    4. Reinstall the nimble package using pip.

    Example usage:
    >>> nbcli legacy update

    Note:
    This command is intended to be used within the nimble CLI to facilitate easy updates of the nimble package. It should be used with caution as it directly affects the local installation of the package. It is recommended to ensure that any important data or configurations are backed up before running this command.
    """

    @staticmethod
    def run(cli):
        if cli.config.no_predict or cli.config.answer == "Y":
            os.system(
                " (cd ~/.nimble/nimble/ ; git checkout master ; git pull --ff-only )"
            )
            os.system("pip install -e ~/.nimble/nimble/")

    @staticmethod
    def check_config(config: "nimble.config"):
        if not config.no_predict:
            answer = Prompt.ask(
                "This will update the local nimble package",
                choices=["Y", "N"],
                default="Y",
            )
            config.answer = answer

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        update_parser = parser.add_parser(
            "update", add_help=False, help="""Update nimble """
        )

        nimble.nbnetwork.add_args(update_parser)


class AutocompleteCommand:
    """Show users how to install and run autocompletion for nimble CLI."""

    @staticmethod
    def run(cli):
        print("To enable autocompletion for nimble CLI, run:")
        print("nbcli --print-completion bash >> ~/.bashrc  # For Bash")
        print("nbcli --print-completion zsh >> ~/.zshrc    # For Zsh")
        print("And then run:\nsource ~/.bashrc  # For both Bash and Zsh")

    @staticmethod
    def add_args(parser):
        parser.add_parser(
            "autocomplete",
            help="Instructions for enabling autocompletion for nimble CLI.",
        )

    @staticmethod
    def check_config(config):
        pass
