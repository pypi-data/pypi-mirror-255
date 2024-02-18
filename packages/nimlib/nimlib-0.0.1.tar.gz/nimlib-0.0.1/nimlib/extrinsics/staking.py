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

import nimlib
from rich.prompt import Confirm
from time import sleep
from typing import List, Dict, Union, Optional
from nimlib.utils.balance import Balance


def add_stake_extrinsic(
    nbnetwork: "nimlib.nbnetwork",
    wallet: "nimlib.wallet",
    hotkey_ss58: Optional[str] = None,
    amount: Union[Balance, float] = None,
    wait_for_inclusion: bool = True,
    wait_for_finalization: bool = False,
    predict: bool = False,
) -> bool:
    r"""Adds the specified amount of stake to passed hotkey uid.
    Args:
        wallet (nimlib.wallet):
            nimble wallet object.
        hotkey_ss58 (Optional[str]):
            ss58 address of the hotkey account to stake to
            defaults to the wallet's hotkey.
        amount (Union[Balance, float]):
            Amount to stake as nimble balance, or float interpreted as NIM.
        wait_for_inclusion (bool):
            If set, waits for the extrinsic to enter a block before returning true,
            or returns false if the extrinsic fails to enter the block within the timeout.
        wait_for_finalization (bool):
            If set, waits for the extrinsic to be finalized on the chain before returning true,
            or returns false if the extrinsic fails to be finalized within the timeout.
        predict (bool):
            If true, the call waits for confirmation from the user before proceeding.
    Returns:
        success (bool):
            flag is true if extrinsic was finalized or uncluded in the block.
            If we did not wait for finalization / inclusion, the response is true.

    Raises:
        nimlib.errors.NotRegisteredError:
            If the wallet is not registered on the chain.
        nimlib.errors.NotDelegateError:
            If the hotkey is not a delegate on the chain.
    """
    # Decrypt keys,
    wallet.coldkey

    # Default to wallet's own hotkey if the value is not passed.
    if hotkey_ss58 is None:
        hotkey_ss58 = wallet.hotkey.ss58_address

    # Flag to indicate if we are using the wallet's own hotkey.
    own_hotkey: bool

    with nimlib.__console__.status(
        ":satellite: Syncing with chain: [white]{}[/white] ...".format(
            nbnetwork.network
        )
    ):
        old_balance = nbnetwork.get_balance(wallet.coldkeypub.ss58_address)
        # Get hotkey owner
        hotkey_owner = nbnetwork.get_hotkey_owner(hotkey_ss58)
        own_hotkey = wallet.coldkeypub.ss58_address == hotkey_owner
        if not own_hotkey:
            # This is not the wallet's own hotkey so we are delegating.
            if not nbnetwork.is_hotkey_delegate(hotkey_ss58):
                raise nimlib.errors.NotDelegateError(
                    "Hotkey: {} is not a delegate.".format(hotkey_ss58)
                )

            # Get hotkey take
            hotkey_take = nbnetwork.get_delegate_take(hotkey_ss58)

        # Get current stake
        old_stake = nbnetwork.get_stake_for_coldkey_and_hotkey(
            coldkey_ss58=wallet.coldkeypub.ss58_address, hotkey_ss58=hotkey_ss58
        )

    # Convert to nimlib.Balance
    if amount == None:
        # Stake it all.
        staking_balance = nimlib.Balance.from_nim(old_balance.nim)
    elif not isinstance(amount, nimlib.Balance):
        staking_balance = nimlib.Balance.from_nim(amount)
    else:
        staking_balance = amount

    # Remove existential balance to keep key alive.
    if staking_balance > nimlib.Balance.from_vim(1000):
        staking_balance = staking_balance - nimlib.Balance.from_vim(1000)
    else:
        staking_balance = staking_balance

    # Check enough to stake.
    if staking_balance > old_balance:
        nimlib.__console__.print(
            ":cross_mark: [red]Not enough stake[/red]:[bold white]\n  balance:{}\n  amount: {}\n  coldkey: {}[/bold white]".format(
                old_balance, staking_balance, wallet.name
            )
        )
        return False

    # Ask before moving on.
    if predict:
        if not own_hotkey:
            # We are delegating.
            if not Confirm.ask(
                "Do you want to delegate:[bold white]\n  amount: {}\n  to: {}\n  take: {}\n  owner: {}[/bold white]".format(
                    staking_balance,
                    wallet.hotkey_str,
                    hotkey_take,
                    hotkey_owner,
                )
            ):
                return False
        else:
            if not Confirm.ask(
                "Do you want to stake:[bold white]\n  amount: {}\n  to: {}[/bold white]".format(
                    staking_balance, wallet.hotkey_str
                )
            ):
                return False

    try:
        with nimlib.__console__.status(
            ":satellite: Staking to: [bold white]{}[/bold white] ...".format(
                nbnetwork.network
            )
        ):
            staking_response: bool = __do_add_stake_single(
                nbnetwork=nbnetwork,
                wallet=wallet,
                hotkey_ss58=hotkey_ss58,
                amount=staking_balance,
                wait_for_inclusion=wait_for_inclusion,
                wait_for_finalization=wait_for_finalization,
            )

        if staking_response == True:  # If we successfully staked.
            # We only wait here if we expect finalization.
            if not wait_for_finalization and not wait_for_inclusion:
                return True

            nimlib.__console__.print(
                ":white_heavy_check_mark: [green]Finalized[/green]"
            )
            with nimlib.__console__.status(
                ":satellite: Checking Balance on: [white]{}[/white] ...".format(
                    nbnetwork.network
                )
            ):
                new_balance = nbnetwork.get_balance(
                    address=wallet.coldkeypub.ss58_address
                )
                block = nbnetwork.get_current_block()
                new_stake = nbnetwork.get_stake_for_coldkey_and_hotkey(
                    coldkey_ss58=wallet.coldkeypub.ss58_address,
                    hotkey_ss58=wallet.hotkey.ss58_address,
                    block=block,
                )  # Get current stake

                nimlib.__console__.print(
                    "Balance:\n  [blue]{}[/blue] :arrow_right: [green]{}[/green]".format(
                        old_balance, new_balance
                    )
                )
                nimlib.__console__.print(
                    "Stake:\n  [blue]{}[/blue] :arrow_right: [green]{}[/green]".format(
                        old_stake, new_stake
                    )
                )
                return True
        else:
            nimlib.__console__.print(
                ":cross_mark: [red]Failed[/red]: Error unknown."
            )
            return False

    except nimlib.errors.NotRegisteredError as e:
        nimlib.__console__.print(
            ":cross_mark: [red]Hotkey: {} is not registered.[/red]".format(
                wallet.hotkey_str
            )
        )
        return False
    except nimlib.errors.StakeError as e:
        nimlib.__console__.print(
            ":cross_mark: [red]Stake Error: {}[/red]".format(e)
        )
        return False


def add_stake_multiple_extrinsic(
    nbnetwork: "nimlib.nbnetwork",
    wallet: "nimlib.wallet",
    hotkey_ss58s: List[str],
    amounts: List[Union[Balance, float]] = None,
    wait_for_inclusion: bool = True,
    wait_for_finalization: bool = False,
    predict: bool = False,
) -> bool:
    r"""Adds stake to each hotkey_ss58 in the list, using each amount, from a common coldkey.
    Args:
        wallet (nimlib.wallet):
            nimble wallet object for the coldkey.
        hotkey_ss58s (List[str]):
            List of hotkeys to stake to.
        amounts (List[Union[Balance, float]]):
            List of amounts to stake. If None, stake all to the first hotkey.
        wait_for_inclusion (bool):
            if set, waits for the extrinsic to enter a block before returning true,
            or returns false if the extrinsic fails to enter the block within the timeout.
        wait_for_finalization (bool):
            if set, waits for the extrinsic to be finalized on the chain before returning true,
            or returns false if the extrinsic fails to be finalized within the timeout.
        predict (bool):
            If true, the call waits for confirmation from the user before proceeding.
    Returns:
        success (bool):
            flag is true if extrinsic was finalized or included in the block.
            flag is true if any wallet was staked.
            If we did not wait for finalization / inclusion, the response is true.
    """
    if not isinstance(hotkey_ss58s, list) or not all(
        isinstance(hotkey_ss58, str) for hotkey_ss58 in hotkey_ss58s
    ):
        raise TypeError("hotkey_ss58s must be a list of str")

    if len(hotkey_ss58s) == 0:
        return True

    if amounts is not None and len(amounts) != len(hotkey_ss58s):
        raise ValueError(
            "amounts must be a list of the same length as hotkey_ss58s"
        )

    if amounts is not None and not all(
        isinstance(amount, (Balance, float)) for amount in amounts
    ):
        raise TypeError(
            "amounts must be a [list of nimlib.Balance or float] or None"
        )

    if amounts is None:
        amounts = [None] * len(hotkey_ss58s)
    else:
        # Convert to Balance
        amounts = [
            nimlib.Balance.from_nim(amount)
            if isinstance(amount, float)
            else amount
            for amount in amounts
        ]

        if sum(amount.nim for amount in amounts) == 0:
            # Staking 0 nim
            return True

    # Decrypt coldkey.
    wallet.coldkey

    old_stakes = []
    with nimlib.__console__.status(
        ":satellite: Syncing with chain: [white]{}[/white] ...".format(
            nbnetwork.network
        )
    ):
        old_balance = nbnetwork.get_balance(wallet.coldkeypub.ss58_address)

        # Get the old stakes.
        for hotkey_ss58 in hotkey_ss58s:
            old_stakes.append(
                nbnetwork.get_stake_for_coldkey_and_hotkey(
                    coldkey_ss58=wallet.coldkeypub.ss58_address,
                    hotkey_ss58=hotkey_ss58,
                )
            )

    # Remove existential balance to keep key alive.
    ## Keys must maintain a balance of at least 1000 vim to stay alive.
    total_staking_vim = sum(
        [amount.vim if amount is not None else 0 for amount in amounts]
    )
    if total_staking_vim == 0:
        # Staking all to the first wallet.
        if old_balance.vim > 1000:
            old_balance -= nimlib.Balance.from_vim(1000)

    elif total_staking_vim < 1000:
        # Staking less than 1000 vim to the wallets.
        pass
    else:
        # Staking more than 1000 vim to the wallets.
        ## Reduce the amount to stake to each wallet to keep the balance above 1000 vim.
        percent_reduction = 1 - (1000 / total_staking_vim)
        amounts = [
            Balance.from_nim(amount.nim * percent_reduction)
            for amount in amounts
        ]

    successful_stakes = 0
    for idx, (hotkey_ss58, amount, old_stake) in enumerate(
        zip(hotkey_ss58s, amounts, old_stakes)
    ):
        staking_all = False
        # Convert to nimlib.Balance
        if amount == None:
            # Stake it all.
            staking_balance = nimlib.Balance.from_nim(old_balance.nim)
            staking_all = True
        else:
            # Amounts are cast to balance earlier in the function
            assert isinstance(amount, nimlib.Balance)
            staking_balance = amount

        # Check enough to stake
        if staking_balance > old_balance:
            nimlib.__console__.print(
                ":cross_mark: [red]Not enough balance[/red]: [green]{}[/green] to stake: [blue]{}[/blue] from coldkey: [white]{}[/white]".format(
                    old_balance, staking_balance, wallet.name
                )
            )
            continue

        # Ask before moving on.
        if predict:
            if not Confirm.ask(
                "Do you want to stake:\n[bold white]  amount: {}\n  hotkey: {}[/bold white ]?".format(
                    staking_balance, wallet.hotkey_str
                )
            ):
                continue

        try:
            staking_response: bool = __do_add_stake_single(
                nbnetwork=nbnetwork,
                wallet=wallet,
                hotkey_ss58=hotkey_ss58,
                amount=staking_balance,
                wait_for_inclusion=wait_for_inclusion,
                wait_for_finalization=wait_for_finalization,
            )

            if staking_response == True:  # If we successfully staked.
                # We only wait here if we expect finalization.

                if idx < len(hotkey_ss58s) - 1:
                    # Wait for tx rate limit.
                    tx_rate_limit_blocks = nbnetwork.tx_rate_limit()
                    if tx_rate_limit_blocks > 0:
                        nimlib.__console__.print(
                            ":hourglass: [yellow]Waiting for tx rate limit: [white]{}[/white] blocks[/yellow]".format(
                                tx_rate_limit_blocks
                            )
                        )
                        sleep(tx_rate_limit_blocks * 12)  # 12 seconds per block

                if not wait_for_finalization and not wait_for_inclusion:
                    old_balance -= staking_balance
                    successful_stakes += 1
                    if staking_all:
                        # If staked all, no need to continue
                        break

                    continue

                nimlib.__console__.print(
                    ":white_heavy_check_mark: [green]Finalized[/green]"
                )

                block = nbnetwork.get_current_block()
                new_stake = nbnetwork.get_stake_for_coldkey_and_hotkey(
                    coldkey_ss58=wallet.coldkeypub.ss58_address,
                    hotkey_ss58=hotkey_ss58,
                    block=block,
                )
                new_balance = nbnetwork.get_balance(
                    wallet.coldkeypub.ss58_address, block=block
                )
                nimlib.__console__.print(
                    "Stake ({}): [blue]{}[/blue] :arrow_right: [green]{}[/green]".format(
                        hotkey_ss58, old_stake, new_stake
                    )
                )
                old_balance = new_balance
                successful_stakes += 1
                if staking_all:
                    # If staked all, no need to continue
                    break

            else:
                nimlib.__console__.print(
                    ":cross_mark: [red]Failed[/red]: Error unknown."
                )
                continue

        except nimlib.errors.NotRegisteredError as e:
            nimlib.__console__.print(
                ":cross_mark: [red]Hotkey: {} is not registered.[/red]".format(
                    hotkey_ss58
                )
            )
            continue
        except nimlib.errors.StakeError as e:
            nimlib.__console__.print(
                ":cross_mark: [red]Stake Error: {}[/red]".format(e)
            )
            continue

    if successful_stakes != 0:
        with nimlib.__console__.status(
            ":satellite: Checking Balance on: ([white]{}[/white] ...".format(
                nbnetwork.network
            )
        ):
            new_balance = nbnetwork.get_balance(wallet.coldkeypub.ss58_address)
        nimlib.__console__.print(
            "Balance: [blue]{}[/blue] :arrow_right: [green]{}[/green]".format(
                old_balance, new_balance
            )
        )
        return True

    return False


def __do_add_stake_single(
    nbnetwork: "nimlib.nbnetwork",
    wallet: "nimlib.wallet",
    hotkey_ss58: str,
    amount: "nimlib.Balance",
    wait_for_inclusion: bool = True,
    wait_for_finalization: bool = False,
) -> bool:
    r"""
    Executes a stake call to the chain using the wallet and amount specified.
    Args:
        wallet (nimlib.wallet):
            nimble wallet object.
        hotkey_ss58 (str):
            Hotkey to stake to.
        amount (nimlib.Balance):
            Amount to stake as nimble balance object.
        wait_for_inclusion (bool):
            If set, waits for the extrinsic to enter a block before returning true,
            or returns false if the extrinsic fails to enter the block within the timeout.
        wait_for_finalization (bool):
            If set, waits for the extrinsic to be finalized on the chain before returning true,
            or returns false if the extrinsic fails to be finalized within the timeout.
        predict (bool):
            If true, the call waits for confirmation from the user before proceeding.
    Returns:
        success (bool):
            flag is true if extrinsic was finalized or uncluded in the block.
            If we did not wait for finalization / inclusion, the response is true.
    Raises:
        nimlib.errors.StakeError:
            If the extrinsic fails to be finalized or included in the block.
        nimlib.errors.NotDelegateError:
            If the hotkey is not a delegate.
        nimlib.errors.NotRegisteredError:
            If the hotkey is not registered in any cosmos.

    """
    # Decrypt keys,
    wallet.coldkey

    hotkey_owner = nbnetwork.get_hotkey_owner(hotkey_ss58)
    own_hotkey = wallet.coldkeypub.ss58_address == hotkey_owner
    if not own_hotkey:
        # We are delegating.
        # Verify that the hotkey is a delegate.
        if not nbnetwork.is_hotkey_delegate(hotkey_ss58=hotkey_ss58):
            raise nimlib.errors.NotDelegateError(
                "Hotkey: {} is not a delegate.".format(hotkey_ss58)
            )

    success = nbnetwork._do_stake(
        wallet=wallet,
        hotkey_ss58=hotkey_ss58,
        amount=amount,
        wait_for_inclusion=wait_for_inclusion,
        wait_for_finalization=wait_for_finalization,
    )

    return success
