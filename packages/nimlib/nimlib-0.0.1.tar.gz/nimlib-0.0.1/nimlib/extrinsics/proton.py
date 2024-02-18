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

import json
from rich.prompt import Confirm
import nimlib.utils.networking as net


def proton_extrinsic(
    nbnetwork: "nimlib.nbnetwork",
    wallet: "nimlib.wallet",
    port: int,
    netuid: int,
    ip: int = None,
    wait_for_inclusion: bool = False,
    wait_for_finalization=True,
) -> bool:
    r"""Subscribes an nimble endpoint to the substensor chain.
    Args:
        nbnetwork (nimlib.nbnetwork):
            nimlib nbnetwork object.
        wallet (nimlib.wallet):
            nimlib wallet object.
        ip (str):
            endpoint host port i.e. 192.122.31.4
        port (int):
            endpoint port number i.e. 9221
        netuid (int):
            network uid to serve on.
        wait_for_inclusion (bool):
            if set, waits for the extrinsic to enter a block before returning true,
            or returns false if the extrinsic fails to enter the block within the timeout.
        wait_for_finalization (bool):
            if set, waits for the extrinsic to be finalized on the chain before returning true,
            or returns false if the extrinsic fails to be finalized within the timeout.
    Returns:
        success (bool):
            flag is true if extrinsic was finalized or uncluded in the block.
            If we did not wait for finalization / inclusion, the response is true.
    """

    # ---- Get external ip ----
    if ip == None:
        try:
            external_ip = net.get_external_ip()
            nimlib.__console__.print(
                ":white_heavy_check_mark: [green]Found external ip: {}[/green]".format(
                    external_ip
                )
            )
            nimlib.logging.success(
                prefix="External IP",
                sufix="<blue>{}</blue>".format(external_ip),
            )
        except Exception as E:
            raise RuntimeError(
                "Unable to attain your external ip. Check your internet connection. error: {}".format(
                    E
                )
            ) from E
    else:
        external_ip = ip

    call_params: "ProtonServeCallParams" = {
        "version": nimlib.__version_as_int__,
        "ip": net.ip_to_int(external_ip),
        "port": port,
        "ip_type": net.ip_version(external_ip),
    }

    with nimlib.__console__.status(":satellite: Checking Proton..."):
        particle = nbnetwork.get_particle_for_pubkey_and_cosmos(
            wallet.hotkey.ss58_address, netuid=netuid
        )
        particle_up_to_date = not particle.is_null and call_params == {
            "version": particle.proton_info.version,
            "ip": net.ip_to_int(particle.proton_info.ip),
            "port": particle.proton_info.port,
            "ip_type": particle.proton_info.ip_type,
        }

    if particle_up_to_date:
        nimlib.__console__.print(
            f":white_heavy_check_mark: [green]Proton already Served[/green]\n"
            f"[green not bold]- Status: [/green not bold] |"
            f"[green not bold] ip: [/green not bold][white not bold]{net.int_to_ip(particle.proton_info.ip)}[/white not bold] |"
            f"[green not bold] ip_type: [/green not bold][white not bold]{particle.proton_info.ip_type}[/white not bold] |"
            f"[green not bold] port: [/green not bold][white not bold]{particle.proton_info.port}[/white not bold] | "
            f"[green not bold] version: [/green not bold][white not bold]{particle.proton_info.version}[/white not bold] |"
        )

        nimlib.__console__.print(
            ":white_heavy_check_mark: [white]Proton already served.[/white]".format(
                external_ip
            )
        )
        return True

    # Add netuid, not in proton_info
    call_params["netuid"] = netuid

    with nimlib.__console__.status(
        ":satellite: Serving proton on: [white]{}:{}[/white] ...".format(
            nbnetwork.network, netuid
        )
    ):
        success, err = nbnetwork._do_serve_proton(
            wallet=wallet,
            call_params=call_params,
            wait_for_finalization=wait_for_finalization,
            wait_for_inclusion=wait_for_inclusion,
        )

        if wait_for_inclusion or wait_for_finalization:
            if success == True:
                nimlib.__console__.print(
                    ":white_heavy_check_mark: [green]Served proton[/green]\n  [bold white]{}[/bold white]".format(
                        json.dumps(call_params, indent=4, sort_keys=True)
                    )
                )
                return True
            else:
                nimlib.__console__.print(
                    ":cross_mark: [green]Failed to serve proton[/green] error: {}".format(
                        err
                    )
                )
                return False
        else:
            return True
