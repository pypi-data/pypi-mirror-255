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

from munch import Munch, munchify

__version__ = "0.0.1"

version_split = __version__.split(".")
__version_as_int__ = (
    (100 * int(version_split[0]))
    + (10 * int(version_split[1]))
    + (1 * int(version_split[2]))
)
__new_signature_version__ = 360

defaults: Munch = munchify(
    {
        "netuid": 1,
        "nbnetwork": {
            "network": "nimble",
            "chain_endpoint": None,
            "_mock": False,
        },
        "pow_register": {
            "num_processes": None,
            "update_interval": 50000,
            "output_in_place": True,
            "verbose": False,
            "cuda": {"dev_id": [0], "use_cuda": False, "tpb": 256},
        },
        "fermion": {
            "port": 8091,
            "ip": "[::]",
            "external_port": None,
            "external_ip": None,
            "max_workers": 10,
            "maximum_concurrent_rpcs": 400,
        },
        "priority": {"max_workers": 5, "maxsize": 10},
        "proton": {"port": 7091, "level": "INFO"},
        "wallet": {
            "name": "default",
            "hotkey": "default",
            "path": "~/.nimble/wallets/",
        },
        "dataset": {
            "batch_size": 10,
            "block_size": 20,
            "num_workers": 0,
            "dataset_names": "default",
            "data_dir": "~/.nimble/data/",
            "save_dataset": False,
            "max_datasets": 3,
            "num_batches": 100,
        },
        "logging": {
            "debug": False,
            "trace": False,
            "record_log": False,
            "logging_dir": "~/.nimble/miners",
        },
    }
)

from .stake import StakeCommand, StakeShow
from .unstake import UnStakeCommand
from .overview import OverviewCommand
from .list import ListCommand
from .register import (
    RegisterCommand,
)
from .wallets import (
    NewColdkeyCommand,
    NewHotkeyCommand,
    RegenColdkeyCommand,
    RegenColdkeypubCommand,
    RegenHotkeyCommand,
    UpdateWalletCommand,
    WalletCreateCommand,
    WalletBalanceCommand,
)
from .transfer import TransferCommand
