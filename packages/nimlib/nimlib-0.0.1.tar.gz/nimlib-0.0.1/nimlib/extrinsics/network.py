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

import time

from rich.prompt import Confirm

import nimlib


def register_cosmos_extrinsic(
    nbnetwork: "nimlib.nbnetwork",
    wallet: "nimlib.wallet",
    wait_for_inclusion: bool = False,
    wait_for_finalization: bool = True,
    predict: bool = False,
) -> bool:
    r"""Registers a new cosmos
    Args:
        wallet (nimlib.wallet):
            nimlib wallet object.
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
            flag is true if extrinsic was finalized or included in the block.
            If we did not wait for finalization / inclusion, the response is true.
    """
    your_balance = nbnetwork.get_balance(wallet.coldkeypub.ss58_address)
    burn_cost = nimlib.utils.balance.Balance(nbnetwork.get_cosmos_burn_cost())
    if burn_cost > your_balance:
        nimlib.__console__.print(
            f"Your balance of: [green]{your_balance}[/green] is not enough to pay the cosmos lock cost of: [green]{burn_cost}[/green]"
        )
        return False

    if predict:
        nimlib.__console__.print(
            f"Your balance is: [green]{your_balance}[/green]"
        )
        if not Confirm.ask(
            f"Do you want to register a cosmos for [green]{ burn_cost }[/green]?"
        ):
            return False

    wallet.coldkey  # unlock coldkey

    with nimlib.__console__.status(":satellite: Registering cosmos..."):
        with nbnetwork.substrate as substrate:
            # create extrinsic call
            call = substrate.compose_call(
                call_module="NbNetworkModule",
                call_function="register_network",
                call_params={"immunity_period": 0, "reg_allowed": True},
            )
            extrinsic = substrate.create_signed_extrinsic(
                call=call, keypair=wallet.coldkey
            )
            response = substrate.submit_extrinsic(
                extrinsic,
                wait_for_inclusion=wait_for_inclusion,
                wait_for_finalization=wait_for_finalization,
            )

            # We only wait here if we expect finalization.
            if not wait_for_finalization and not wait_for_inclusion:
                return True

            # process if registration successful
            response.process_events()
            if not response.is_success:
                nimlib.__console__.print(
                    ":cross_mark: [red]Failed[/red]: error:{}".format(
                        response.error_message
                    )
                )
                time.sleep(0.5)

            # Successful registration, final check for membership
            else:
                nimlib.__console__.print(
                    f":white_heavy_check_mark: [green]Registered cosmos with netuid: {response.triggered_events[1].value['event']['attributes'][0]}[/green]"
                )
                return True
