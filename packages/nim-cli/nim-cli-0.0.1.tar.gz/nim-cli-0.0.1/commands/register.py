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
import argparse
import nimble
from rich.prompt import Prompt, Confirm
from .utils import check_netuid_set

from . import defaults

console = nimble.__console__


class RegisterCommand:
    """
    Executes the 'register' command to register a neuron on the nimble network by recycling some NIM (the network's native token).
    This command is used to add a new neuron to a specified subnet within the network, contributing to the decentralization and robustness of nimble.

    Usage:
    Before registering, the command checks if the specified subnet exists and whether the user's balance is sufficient to cover the registration cost.
    The registration cost is determined by the current recycle amount for the specified subnet. If the balance is insufficient or the subnet does not exist,
    the command will exit with an appropriate error message.

    If the preconditions are met, and the user confirms the transaction (if 'no_prompt' is not set), the command proceeds to register the neuron by burning the required amount of NIM.

    The command structure includes:
    - Verification of subnet existence.
    - Checking the user's balance against the current recycle amount for the subnet.
    - User confirmation prompt for proceeding with registration.
    - Execution of the registration process.

    Columns Displayed in the Confirmation Prompt:
    - Balance: The current balance of the user's wallet in NIM.
    - Cost to Register: The required amount of NIM needed to register on the specified subnet.

    Example usage:
    >>> nbcli subnets register --netuid 1

    Note:
    This command is critical for users who wish to contribute a new neuron to the network. It requires careful consideration of the subnet selection and
    an understanding of the registration costs. Users should ensure their wallet is sufficiently funded before attempting to register a neuron.
    """

    @staticmethod
    def run(cli):
        r"""Register neuron by recycling some NIM."""
        wallet = nimble.wallet(config=cli.config)
        nbnetwork = nimble.nbnetwork(config=cli.config, log_verbose=False)

        # Verify subnet exists
        if not nbnetwork.cosmos_exists(netuid=cli.config.netuid):
            nimble.__console__.print(
                f"[red]Subnet {cli.config.netuid} does not exist[/red]"
            )
            sys.exit(1)

        # Check current recycle amount
        current_recycle = nbnetwork.burn(netuid=cli.config.netuid)
        balance = nbnetwork.get_balance(address=wallet.coldkeypub.ss58_address)

        # Check balance is sufficient
        if balance < current_recycle:
            nimble.__console__.print(
                f"[red]Insufficient balance {balance} to register neuron. Current recycle is {current_recycle} NIM[/red]"
            )
            sys.exit(1)

        if not cli.config.no_prompt:
            if (
                Confirm.ask(
                    f"Your balance is: [bold green]{balance}[/bold green]\nThe cost to register by recycle is [bold red]{current_recycle}[/bold red]\nDo you want to continue?",
                    default=False,
                )
                == False
            ):
                sys.exit(1)

        nbnetwork.burned_register(
            wallet=wallet,
            netuid=cli.config.netuid,
            prompt=not cli.config.no_prompt,
        )

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        register_parser = parser.add_parser(
            "register", help="""Register a wallet to a network."""
        )
        register_parser.add_argument(
            "--netuid",
            type=int,
            help="netuid for subnet to serve this neuron on",
            default=argparse.SUPPRESS,
        )

        nimble.wallet.add_args(register_parser)
        nimble.nbnetwork.add_args(register_parser)

    @staticmethod
    def check_config(config: "nimble.config"):
        if (
            not config.is_set("nbnetwork.network")
            and not config.is_set("nbnetwork.chain_endpoint")
            and not config.no_prompt
        ):
            config.nbnetwork.network = Prompt.ask(
                "Enter nbnetwork network",
                choices=nimble.__networks__,
                default=defaults.nbnetwork.network,
            )
            _, endpoint = nimble.nbnetwork.determine_chain_endpoint_and_network(
                config.nbnetwork.network
            )
            config.nbnetwork.chain_endpoint = endpoint

        check_netuid_set(
            config, nbnetwork=nimble.nbnetwork(config=config, log_verbose=False)
        )

        if not config.is_set("wallet.name") and not config.no_prompt:
            wallet_name = Prompt.ask("Enter wallet name", default=defaults.wallet.name)
            config.wallet.name = str(wallet_name)

        if not config.is_set("wallet.hotkey") and not config.no_prompt:
            hotkey = Prompt.ask("Enter hotkey name", default=defaults.wallet.hotkey)
            config.wallet.hotkey = str(hotkey)
