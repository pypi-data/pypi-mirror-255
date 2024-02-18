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
import json
import nimlib
from dataclasses import asdict
import nimlib.utils.networking as net
from rich.prompt import Confirm
from ..errors import MetadataError


def serve_extrinsic(
    nbnetwork: "nimlib.nbnetwork",
    wallet: "nimlib.wallet",
    ip: str,
    port: int,
    protocol: int,
    netuid: int,
    placeholder1: int = 0,
    placeholder2: int = 0,
    wait_for_inclusion: bool = False,
    wait_for_finalization=True,
    predict: bool = False,
) -> bool:
    r"""Subscribes a nimble endpoint to the substensor chain.
    Args:
        wallet (nimlib.wallet):
            nimble wallet object.
        ip (str):
            endpoint host port i.e. 192.122.31.4
        port (int):
            endpoint port number i.e. 9221
        protocol (int):
            int representation of the protocol
        netuid (int):
            network uid to serve on.
        placeholder1 (int):
            placeholder for future use.
        placeholder2 (int):
            placeholder for future use.
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
            flag is true if extrinsic was finalized or uncluded in the block.
            If we did not wait for finalization / inclusion, the response is true.
    """
    # Decrypt hotkey
    wallet.hotkey
    params: "FermionServeCallParams" = {
        "version": nimlib.__version_as_int__,
        "ip": net.ip_to_int(ip),
        "port": port,
        "ip_type": net.ip_version(ip),
        "netuid": netuid,
        "hotkey": wallet.hotkey.ss58_address,
        "coldkey": wallet.coldkeypub.ss58_address,
        "protocol": protocol,
        "placeholder1": placeholder1,
        "placeholder2": placeholder2,
    }
    nimlib.logging.debug("Checking fermion ...")
    particle = nbnetwork.get_particle_for_pubkey_and_cosmos(
        wallet.hotkey.ss58_address, netuid=netuid
    )
    particle_up_to_date = not particle.is_null and params == {
        "version": particle.fermion_info.version,
        "ip": net.ip_to_int(particle.fermion_info.ip),
        "port": particle.fermion_info.port,
        "ip_type": particle.fermion_info.ip_type,
        "netuid": particle.netuid,
        "hotkey": particle.hotkey,
        "coldkey": particle.coldkey,
        "protocol": particle.fermion_info.protocol,
        "placeholder1": particle.fermion_info.placeholder1,
        "placeholder2": particle.fermion_info.placeholder2,
    }
    output = params.copy()
    output["coldkey"] = wallet.coldkeypub.ss58_address
    output["hotkey"] = wallet.hotkey.ss58_address
    if particle_up_to_date:
        nimlib.logging.debug(
            f"Fermion already served on: FermionInfo({wallet.hotkey.ss58_address},{ip}:{port}) "
        )
        return True

    if predict:
        output = params.copy()
        output["coldkey"] = wallet.coldkeypub.ss58_address
        output["hotkey"] = wallet.hotkey.ss58_address
        if not Confirm.ask(
            "Do you want to serve fermion:\n  [bold white]{}[/bold white]".format(
                json.dumps(output, indent=4, sort_keys=True)
            )
        ):
            return False

    nimlib.logging.debug(
        f"Serving fermion with: FermionInfo({wallet.hotkey.ss58_address},{ip}:{port}) -> {nbnetwork.network}:{netuid}"
    )
    success, error_message = nbnetwork._do_serve_fermion(
        wallet=wallet,
        call_params=params,
        wait_for_finalization=wait_for_finalization,
        wait_for_inclusion=wait_for_inclusion,
    )

    if wait_for_inclusion or wait_for_finalization:
        if success == True:
            nimlib.logging.debug(
                f"Fermion served with: FermionInfo({wallet.hotkey.ss58_address},{ip}:{port}) on {nbnetwork.network}:{netuid} "
            )
            return True
        else:
            nimlib.logging.debug(
                f"Fermion failed to served with error: {error_message} "
            )
            return False
    else:
        return True


def serve_fermion_extrinsic(
    nbnetwork: "nimlib.nbnetwork",
    netuid: int,
    fermion: "nimlib.Fermion",
    wait_for_inclusion: bool = False,
    wait_for_finalization: bool = True,
    predict: bool = False,
) -> bool:
    r"""Serves the fermion to the network.
    Args:
        netuid ( int ):
            The netuid being served on.
        fermion (nimlib.Fermion):
            Fermion to serve.
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
    """
    fermion.wallet.hotkey
    fermion.wallet.coldkeypub
    external_port = fermion.external_port

    # ---- Get external ip ----
    if fermion.external_ip == None:
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
        external_ip = fermion.external_ip

    # ---- Subscribe to chain ----
    serve_success = nbnetwork.serve(
        wallet=fermion.wallet,
        ip=external_ip,
        port=external_port,
        netuid=netuid,
        protocol=4,
        wait_for_inclusion=wait_for_inclusion,
        wait_for_finalization=wait_for_finalization,
        predict=predict,
    )
    return serve_success


def publish_metadata(
    nbnetwork: "nimlib.nbnetwork",
    wallet: "nimlib.wallet",
    netuid: int,
    type: str,
    data: str,
    wait_for_inclusion: bool = False,
    wait_for_finalization: bool = True,
) -> bool:
    """
    Publishes metadata on the nimble network using the specified wallet and network identifier.

    Args:
        nbnetwork (nimlib.nbnetwork):
            The nbnetwork instance representing the nimlib blockchain connection.
        wallet (nimlib.wallet):
            The wallet object used for authentication in the transaction.
        netuid (int):
            Network UID on which the metadata is to be published.
        type (str):
            The data type of the information being submitted. It should be one of the following:
            'Sha256', 'Blake256', 'Keccak256', or 'Raw0-128'. This specifies the format or
            hashing algorithm used for the data.
        data (str):
            The actual metadata content to be published. This should be formatted or hashed
            according to the 'type' specified. (Note: max str length of 128 bytes)
        wait_for_inclusion (bool, optional):
            If True, the function will wait for the extrinsic to be included in a block before returning.
            Defaults to False.
        wait_for_finalization (bool, optional):
            If True, the function will wait for the extrinsic to be finalized on the chain before returning.
            Defaults to True.

    Returns:
        bool:
            True if the metadata was successfully published (and finalized if specified). False otherwise.

    Raises:
        MetadataError:
            If there is an error in submitting the extrinsic or if the response from the blockchain indicates failure.
    """

    wallet.hotkey

    with nbnetwork.substrate as substrate:
        call = substrate.compose_call(
            call_module="Commitments",
            call_function="set_commitment",
            call_params={
                "netuid": netuid,
                "info": {"fields": [[{f"{type}": data}]]},
            },
        )

        extrinsic = substrate.create_signed_extrinsic(
            call=call, keypair=wallet.hotkey
        )
        response = substrate.submit_extrinsic(
            extrinsic,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
        )
        # We only wait here if we expect finalization.
        if not wait_for_finalization and not wait_for_inclusion:
            return True
        response.process_events()
        if response.is_success:
            return True
        else:
            raise MetadataError(response.error_message)


from retry import retry
from typing import Optional


def get_metadata(
    self, netuid: int, hotkey: str, block: Optional[int] = None
) -> str:
    @retry(delay=2, tries=3, backoff=2, max_delay=4)
    def make_substrate_call_with_retry():
        with self.substrate as substrate:
            return substrate.query(
                module="Commitments",
                storage_function="CommitmentOf",
                params=[netuid, hotkey],
                block_hash=None
                if block == None
                else substrate.get_block_hash(block),
            )

    commit_data = make_substrate_call_with_retry()
    return commit_data.value
