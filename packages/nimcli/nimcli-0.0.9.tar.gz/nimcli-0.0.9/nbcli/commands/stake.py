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

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional, Dict
from typing import Union

import nimlib as nimble
from nimlib import defaults
from nimlib.utils.balance import Balance
from rich.prompt import Confirm
from rich.prompt import Prompt
from rich.table import Table
from tqdm import tqdm

from .utils import get_delegates_details, DelegatesDetails
from .utils import get_hotkey_wallets_for_wallet

console = nimble.__console__


class StakeCommand:
    """
    Executes the 'add' command to stake tokens to one or more hotkeys from a user's coldkey on the nimble network.
    This command is used to allocate tokens to different hotkeys, securing their position and influence on the network.

    Usage:
    Users can specify the amount to stake, the hotkeys to stake to (either by name or SS58 address),
    and whether to stake to all hotkeys. The command checks for sufficient balance and hotkey registration
    before proceeding with the staking process.

    Optional arguments:
    - --all (bool): When set, stakes all available tokens from the coldkey.
    - --uid (int): The unique identifier of the particle to which the stake is to be added.
    - --amount (float): The amount of NIM tokens to stake.
    - --max_stake (float): Sets the maximum amount of NIM to have staked in each hotkey.
    - --hotkeys (list): Specifies hotkeys by name or SS58 address to stake to.
    - --all_hotkeys (bool): When set, stakes to all hotkeys associated with the wallet, excluding any specified in --hotkeys.

    The command asks for confirmation before executing the staking operation.

    Example usage:
    >>> nimcli stake add --amount 100 --wallet.name <my_wallet> --wallet.hotkey <my_hotkey>

    Note:
    This command is critical for users who wish to distribute their stakes among different particles (hotkeys) on the network.
    It allows for a strategic allocation of tokens to enhance network participation and influence.
    """

    @staticmethod
    def run(cli):
        r"""Stake token of amount to hotkey(s)."""
        config = cli.config.copy()
        wallet = nimble.wallet(config=config)
        nbnetwork: nimble.nbnetwork = nimble.nbnetwork(config=config, log_verbose=False)

        # Get the hotkey_names (if any) and the hotkey_ss58s.
        hotkeys_to_stake_to: List[Tuple[Optional[str], str]] = []
        if config.get("all_hotkeys"):
            # Stake to all hotkeys.
            all_hotkeys: List[nimble.wallet] = get_hotkey_wallets_for_wallet(
                wallet=wallet
            )
            # Get the hotkeys to exclude. (d)efault to no exclusions.
            hotkeys_to_exclude: List[str] = cli.config.get("hotkeys", d=[])
            # Exclude hotkeys that are specified.
            hotkeys_to_stake_to = [
                (wallet.hotkey_str, wallet.hotkey.ss58_address)
                for wallet in all_hotkeys
                if wallet.hotkey_str not in hotkeys_to_exclude
            ]  # definitely wallets

        elif config.get("hotkeys"):
            # Stake to specific hotkeys.
            for hotkey_ss58_or_hotkey_name in config.get("hotkeys"):
                if nimble.utils.is_valid_ss58_address(hotkey_ss58_or_hotkey_name):
                    # If the hotkey is a valid ss58 address, we add it to the list.
                    hotkeys_to_stake_to.append((None, hotkey_ss58_or_hotkey_name))
                else:
                    # If the hotkey is not a valid ss58 address, we assume it is a hotkey name.
                    #  We then get the hotkey from the wallet and add it to the list.
                    wallet_ = nimble.wallet(
                        config=config, hotkey=hotkey_ss58_or_hotkey_name
                    )
                    hotkeys_to_stake_to.append(
                        (wallet_.hotkey_str, wallet_.hotkey.ss58_address)
                    )
        elif config.wallet.get("hotkey"):
            # Only config.wallet.hotkey is specified.
            #  so we stake to that single hotkey.
            hotkey_ss58_or_name = config.wallet.get("hotkey")
            if nimble.utils.is_valid_ss58_address(hotkey_ss58_or_name):
                hotkeys_to_stake_to = [(None, hotkey_ss58_or_name)]
            else:
                # Hotkey is not a valid ss58 address, so we assume it is a hotkey name.
                wallet_ = nimble.wallet(config=config, hotkey=hotkey_ss58_or_name)
                hotkeys_to_stake_to = [
                    (wallet_.hotkey_str, wallet_.hotkey.ss58_address)
                ]
        else:
            # Only config.wallet.hotkey is specified.
            #  so we stake to that single hotkey.
            assert config.wallet.hotkey is not None
            hotkeys_to_stake_to = [
                (None, nimble.wallet(config=config).hotkey.ss58_address)
            ]

        # Get coldkey balance
        wallet_balance: Balance = nbnetwork.get_balance(wallet.coldkeypub.ss58_address)
        final_hotkeys: List[Tuple[str, str]] = []
        final_amounts: List[Union[float, Balance]] = []
        for hotkey in tqdm(hotkeys_to_stake_to):
            hotkey: Tuple[Optional[str], str]  # (hotkey_name (or None), hotkey_ss58)
            if not nbnetwork.is_hotkey_registered_any(hotkey_ss58=hotkey[1]):
                # Hotkey is not registered.
                if len(hotkeys_to_stake_to) == 1:
                    # Only one hotkey, error
                    nimble.__console__.print(
                        f"[red]Hotkey [bold]{hotkey[1]}[/bold] is not registered. Aborting.[/red]"
                    )
                    return None
                else:
                    # Otherwise, print warning and skip
                    nimble.__console__.print(
                        f"[yellow]Hotkey [bold]{hotkey[1]}[/bold] is not registered. Skipping.[/yellow]"
                    )
                    continue

            stake_amount_nim: float = config.get("amount")
            if config.get("max_stake"):
                # Get the current stake of the hotkey from this coldkey.
                hotkey_stake: Balance = nbnetwork.get_stake_for_coldkey_and_hotkey(
                    hotkey_ss58=hotkey[1],
                    coldkey_ss58=wallet.coldkeypub.ss58_address,
                )
                stake_amount_nim: float = config.get("max_stake") - hotkey_stake.nim

                # If the max_stake is greater than the current wallet balance, stake the entire balance.
                stake_amount_nim: float = min(stake_amount_nim, wallet_balance.nim)
                if (
                    stake_amount_nim <= 0.00001
                ):  # Threshold because of fees, might create a loop otherwise
                    # Skip hotkey if max_stake is less than current stake.
                    continue
                wallet_balance = Balance.from_nim(wallet_balance.nim - stake_amount_nim)

                if wallet_balance.nim < 0:
                    # No more balance to stake.
                    break

            final_amounts.append(stake_amount_nim)
            final_hotkeys.append(hotkey)  # add both the name and the ss58 address.

        if len(final_hotkeys) == 0:
            # No hotkeys to stake to.
            nimble.__console__.print(
                "Not enough balance to stake to any hotkeys or max_stake is less than current stake."
            )
            return None

        # Ask to stake
        if not config.no_predict:
            if not Confirm.ask(
                f"Do you want to stake to the following keys from {wallet.name}:\n"
                + "".join(
                    [
                        f"    [bold white]- {hotkey[0] + ':' if hotkey[0] else ''}{hotkey[1]}: {f'{amount} {nimble.__nim_symbol__}' if amount else 'All'}[/bold white]\n"
                        for hotkey, amount in zip(final_hotkeys, final_amounts)
                    ]
                )
            ):
                return None

        if len(final_hotkeys) == 1:
            # do regular stake
            return nbnetwork.add_stake(
                wallet=wallet,
                hotkey_ss58=final_hotkeys[0][1],
                amount=None if config.get("stake_all") else final_amounts[0],
                wait_for_inclusion=True,
                predict=not config.no_predict,
            )

        nbnetwork.add_stake_multiple(
            wallet=wallet,
            hotkey_ss58s=[hotkey_ss58 for _, hotkey_ss58 in final_hotkeys],
            amounts=None if config.get("stake_all") else final_amounts,
            wait_for_inclusion=True,
            predict=False,
        )

    @classmethod
    def check_config(cls, config: "nimble.config"):
        if not config.is_set("wallet.name") and not config.no_predict:
            wallet_name = Prompt.ask("Enter wallet name", default=defaults.wallet.name)
            config.wallet.name = str(wallet_name)

        if (
            not config.is_set("wallet.hotkey")
            and not config.no_predict
            and not config.wallet.get("all_hotkeys")
            and not config.wallet.get("hotkeys")
        ):
            hotkey = Prompt.ask("Enter hotkey name", default=defaults.wallet.hotkey)
            config.wallet.hotkey = str(hotkey)

        # Get amount.
        if (
            not config.get("amount")
            and not config.get("stake_all")
            and not config.get("max_stake")
        ):
            if not Confirm.ask(
                "Stake all NIM from account: [bold]'{}'[/bold]?".format(
                    config.wallet.get("name", defaults.wallet.name)
                )
            ):
                amount = Prompt.ask("Enter NIM amount to stake")
                try:
                    config.amount = float(amount)
                except ValueError:
                    console.print(
                        ":cross_mark:[red]Invalid Nim amount[/red] [bold white]{}[/bold white]".format(
                            amount
                        )
                    )
                    sys.exit()
            else:
                config.stake_all = True

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        stake_parser = parser.add_parser(
            "add",
            help="""Add stake to your hotkey accounts from your coldkey.""",
        )
        stake_parser.add_argument("--all", dest="stake_all", action="store_true")
        stake_parser.add_argument("--uid", dest="uid", type=int, required=False)
        stake_parser.add_argument("--amount", dest="amount", type=float, required=False)
        stake_parser.add_argument(
            "--max_stake",
            dest="max_stake",
            type=float,
            required=False,
            action="store",
            default=None,
            help="""Specify the maximum amount of Nim to have staked in each hotkey.""",
        )
        stake_parser.add_argument(
            "--hotkeys",
            "--exclude_hotkeys",
            "--wallet.hotkeys",
            "--wallet.exclude_hotkeys",
            required=False,
            action="store",
            default=[],
            type=str,
            nargs="*",
            help="""Specify the hotkeys by name or ss58 address. (e.g. hk1 hk2 hk3)""",
        )
        stake_parser.add_argument(
            "--all_hotkeys",
            "--wallet.all_hotkeys",
            required=False,
            action="store_true",
            default=False,
            help="""To specify all hotkeys. Specifying hotkeys will exclude them from this all.""",
        )
        nimble.wallet.add_args(stake_parser)
        nimble.nbnetwork.add_args(stake_parser)


### Stake list.
def _get_coldkey_wallets_for_path(path: str) -> List["nimble.wallet"]:
    try:
        wallet_names = next(os.walk(os.path.expanduser(path)))[1]
        return [nimble.wallet(path=path, name=name) for name in wallet_names]
    except StopIteration:
        # No wallet files found.
        wallets = []
    return wallets


def _get_hotkey_wallets_for_wallet(wallet) -> List["nimble.wallet"]:
    hotkey_wallets = []
    hotkeys_path = wallet.path + "/" + wallet.name + "/hotkeys"
    try:
        hotkey_files = next(os.walk(os.path.expanduser(hotkeys_path)))[2]
    except StopIteration:
        hotkey_files = []
    for hotkey_file_name in hotkey_files:
        try:
            hotkey_for_name = nimble.wallet(
                path=wallet.path, name=wallet.name, hotkey=hotkey_file_name
            )
            if (
                hotkey_for_name.hotkey_file.exists_on_device()
                and not hotkey_for_name.hotkey_file.is_encrypted()
            ):
                hotkey_wallets.append(hotkey_for_name)
        except Exception:
            pass
    return hotkey_wallets


class StakeShow:
    """
    Executes the 'show' command to list all stake accounts associated with a user's wallet on the nimble network.
    This command provides a comprehensive view of the stakes associated with both hotkeys and delegates linked to the user's coldkey.

    Usage:
    The command lists all stake accounts for a specified wallet or all wallets in the user's configuration directory.
    It displays the coldkey, balance, account details (hotkey/delegate name), stake amount, and the rate of return.

    Optional arguments:
    - --all (bool): When set, the command checks all coldkey wallets instead of just the specified wallet.

    The command compiles a table showing:
    - Coldkey: The coldkey associated with the wallet.
    - Balance: The balance of the coldkey.
    - Account: The name of the hotkey or delegate.
    - Stake: The amount of NIM staked to the hotkey or delegate.
    - Rate: The rate of return on the stake, typically shown in NIM per day.

    Example usage:
    >>> nimcli stake show --all

    Note:
    This command is essential for users who wish to monitor their stake distribution and returns across various accounts on the nimble network.
    It provides a clear and detailed overview of the user's staking activities.
    """

    @staticmethod
    def run(cli):
        r"""Show all stake accounts."""
        if cli.config.get("all", d=False) == True:
            wallets = _get_coldkey_wallets_for_path(cli.config.wallet.path)
        else:
            wallets = [nimble.wallet(config=cli.config)]
        registered_delegate_info: Optional[
            Dict[str, DelegatesDetails]
        ] = get_delegates_details(url=nimble.__delegates_details_url__)

        def get_stake_accounts(
            wallet,
        ) -> Dict[str, Dict[str, Union[str, Balance]]]:
            """Get stake account details for the given wallet.

            Args:
                wallet: The wallet object to fetch the stake account details for.

            Returns:
                A dictionary mapping SS58 addresses to their respective stake account details.
            """
            nbnetwork = nimble.nbnetwork(config=cli.config, log_verbose=False)

            wallet_stake_accounts = {}

            # Get this wallet's coldkey balance.
            cold_balance = nbnetwork.get_balance(wallet.coldkeypub.ss58_address)

            # Populate the stake accounts with local hotkeys data.
            wallet_stake_accounts.update(get_stakes_from_hotkeys(nbnetwork, wallet))

            # Populate the stake accounts with delegations data.
            wallet_stake_accounts.update(get_stakes_from_delegates(nbnetwork, wallet))

            return {
                "name": wallet.name,
                "balance": cold_balance,
                "accounts": wallet_stake_accounts,
            }

        def get_stakes_from_hotkeys(
            nbnetwork, wallet
        ) -> Dict[str, Dict[str, Union[str, Balance]]]:
            """Fetch stakes from hotkeys for the provided wallet.

            Args:
                wallet: The wallet object to fetch the stakes for.

            Returns:
                A dictionary of stakes related to hotkeys.
            """
            hotkeys = get_hotkey_wallets_for_wallet(wallet)
            stakes = {}
            for hot in hotkeys:
                emission = sum(
                    [
                        n.emission
                        for n in nbnetwork.get_all_particles_for_pubkey(
                            hot.hotkey.ss58_address
                        )
                    ]
                )
                hotkey_stake = nbnetwork.get_stake_for_coldkey_and_hotkey(
                    hotkey_ss58=hot.hotkey.ss58_address,
                    coldkey_ss58=wallet.coldkeypub.ss58_address,
                )
                stakes[hot.hotkey.ss58_address] = {
                    "name": hot.hotkey_str,
                    "stake": hotkey_stake,
                    "rate": emission,
                }
            return stakes

        def get_stakes_from_delegates(
            nbnetwork, wallet
        ) -> Dict[str, Dict[str, Union[str, Balance]]]:
            """Fetch stakes from delegates for the provided wallet.

            Args:
                wallet: The wallet object to fetch the stakes for.

            Returns:
                A dictionary of stakes related to delegates.
            """
            delegates = nbnetwork.get_delegated(
                coldkey_ss58=wallet.coldkeypub.ss58_address
            )
            stakes = {}
            for dele, staked in delegates:
                for nom in dele.nominators:
                    if nom[0] == wallet.coldkeypub.ss58_address:
                        delegate_name = (
                            registered_delegate_info[dele.hotkey_ss58].name
                            if dele.hotkey_ss58 in registered_delegate_info
                            else dele.hotkey_ss58
                        )
                        stakes[dele.hotkey_ss58] = {
                            "name": delegate_name,
                            "stake": nom[1],
                            "rate": dele.total_daily_return.nim
                            * (nom[1] / dele.total_stake.nim),
                        }
            return stakes

        def get_all_wallet_accounts(
            wallets,
        ) -> List[Dict[str, Dict[str, Union[str, Balance]]]]:
            """Fetch stake accounts for all provided wallets using a ThreadPool.

            Args:
                wallets: List of wallets to fetch the stake accounts for.

            Returns:
                A list of dictionaries, each dictionary containing stake account details for each wallet.
            """

            accounts = []
            # Create a progress bar using tqdm
            with tqdm(total=len(wallets), desc="Fetching accounts", ncols=100) as pbar:
                # Using a ThreadPool to fetch accounts.
                with ThreadPoolExecutor() as executor:
                    for account in executor.map(get_stake_accounts, wallets):
                        accounts.append(account)
                        pbar.update()
            return accounts

        accounts = get_all_wallet_accounts(wallets)

        total_stake = 0
        total_balance = 0
        total_rate = 0
        for acc in accounts:
            total_balance += acc["balance"].nim
            for key, value in acc["accounts"].items():
                total_stake += value["stake"].nim
                total_rate += float(value["rate"])
        table = Table(show_footer=True, pad_edge=False, box=None, expand=False)
        table.add_column(
            "[overline white]Coldkey",
            footer_style="overline white",
            style="bold white",
        )
        table.add_column(
            "[overline white]Balance",
            "nim{:.5f}".format(total_balance),
            footer_style="overline white",
            style="green",
        )
        table.add_column(
            "[overline white]Account",
            footer_style="overline white",
            style="blue",
        )
        table.add_column(
            "[overline white]Stake",
            "nim{:.5f}".format(total_stake),
            footer_style="overline white",
            style="green",
        )
        table.add_column(
            "[overline white]Rate",
            "nim{:.5f}/d".format(total_rate),
            footer_style="overline white",
            style="green",
        )
        for acc in accounts:
            table.add_row(acc["name"], acc["balance"], "", "")
            for key, value in acc["accounts"].items():
                table.add_row(
                    "",
                    "",
                    value["name"],
                    value["stake"],
                    str(value["rate"]) + "/d",
                )
        nimble.__console__.print(table)

    @staticmethod
    def check_config(config: "nimble.config"):
        if (
            not config.get("all", d=None)
            and not config.is_set("wallet.name")
            and not config.no_predict
        ):
            wallet_name = Prompt.ask("Enter wallet name", default=defaults.wallet.name)
            config.wallet.name = str(wallet_name)

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        list_parser = parser.add_parser(
            "show", help="""List all stake accounts for wallet."""
        )
        list_parser.add_argument(
            "--all",
            action="store_true",
            help="""Check all coldkey wallets.""",
            default=False,
        )

        nimble.wallet.add_args(list_parser)
        nimble.nbnetwork.add_args(list_parser)
