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
import copy
import os
from typing import List, Dict, Union, Optional, Tuple, Any

import scalecodec
from loguru import logger
from retry import retry
from scalecodec.base import RuntimeConfiguration
from scalecodec.type_registry import load_type_registry_preset
from substrateinterface.base import QueryMapResult, SubstrateInterface

import nimlib

# Local imports.
from .chain_data import (
    ParticleInfo,
    CosmosInfo,
    CosmosHyperparameters,
    StakeInfo,
    ParticleInfoLite,
    FermionInfo,
    IPInfo,
    custom_rpc_type_registry,
)
from .errors import *
from .extrinsics.serving import (
    serve_extrinsic,
    serve_fermion_extrinsic,
)
from .extrinsics.staking import (
    add_stake_extrinsic,
    add_stake_multiple_extrinsic,
)
from .extrinsics.registration import (
    register_extrinsic,
    burned_register_extrinsic,
)
from .extrinsics.transfer import transfer_extrinsic
from .extrinsics.unstaking import unstake_extrinsic, unstake_multiple_extrinsic
from .types import FermionServeCallParams, ParamWithTypes
from .utils import ss58_to_vec_u8
from .utils.balance import Balance

logger = logger.opt(colors=True)


class NimbleNetwork:
    """
    The NimbleNetwork class in nimble serves as a crucial interface for interacting with the nimble blockchain,
    facilitating a range of operations essential for the decentralized machine learning network. This class
    enables particles (network participants) to engage in activities such as registering on the network, managing
    staked weights, setting inter-particle weights, and participating in consensus mechanisms.

    The nimble network operates on a digital ledger where each particle holds stakes (S) and learns a set
    of inter-peer weights (W). These weights, set by the particles themselves, play a critical role in determining
    the ranking and incentive mechanisms within the network. Higher-ranked particles, as determined by their
    contributions and trust within the network, receive more incentives.

    The NbNetwork class connects to various nimble networks like the main 'nimble' network or local test
    networks, providing a gateway to the blockchain layer of nimlib. It leverages a staked weighted trust
    system and consensus to ensure fair and distributed incentive mechanisms, where incentives (I) are
    primarily allocated to particles that are trusted by the majority of the network&#8203;``【oaicite:1】``&#8203;.

    Additionally, nimble introduces a speculation-based reward mechanism in the form of bonds (B), allowing
    particles to accumulate bonds in other particles, speculating on their future value. This mechanism aligns
    with market-based speculation, incentivizing particles to make judicious decisions in their inter-particle
    investments.

    Attributes:
        network (str): The name of the nimble network (e.g., 'nimble', 'test', 'archive', 'local') the instance
                       is connected to, determining the blockchain interaction context.
        chain_endpoint (str): The blockchain node endpoint URL, enabling direct communication
                              with the nimble blockchain for transaction processing and data retrieval.

    Example Usage:
        # Connect to the main nimble network (nimble).
        nimble_nbnetwork = nbnetwork(network='nimble')

        # Register a new particle on the network.
        wallet = nimlib.wallet(...)  # Assuming a wallet instance is created.
        success = nimble_nbnetwork.register(wallet=wallet, netuid=netuid)

        # Set inter-particle weights for collaborative learning.
        success = nimble_nbnetwork.set_weights(wallet=wallet, netuid=netuid, uids=[...], weights=[...])

        # Speculate by accumulating bonds in other promising particles.
        success = nimble_nbnetwork.delegate(wallet=wallet, delegate_ss58=other_particle_ss58, amount=bond_amount)

        # Get the megastring for a specific cosmos using given nbnetwork connection
        megastring = nbnetwork.megastring(netuid=netuid)

    By facilitating these operations, the NbNetwork class is instrumental in maintaining the decentralized
    intelligence and dynamic learning environment of the nimble network, as envisioned in its foundational
    principles and mechanisms described in the NeurIPS paper.
    """

    @staticmethod
    def config() -> "nimlib.config":
        parser = argparse.ArgumentParser()
        NimbleNetwork.add_args(parser)
        return nimlib.config(parser, args=[])

    @classmethod
    def help(cls):
        """Print help to stdout"""
        parser = argparse.ArgumentParser()
        cls.add_args(parser)
        print(cls.__new__.__doc__)
        parser.print_help()

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser, prefix: str = None):
        prefix_str = "" if prefix == None else prefix + "."
        try:
            default_network = os.getenv("NB_NETWORK") or "nimble"
            default_chain_endpoint = (
                os.getenv("NB_NETWORK_CHAIN_ENDPOINT")
                or nimlib.__nimble_entrypoint__
            )
            parser.add_argument(
                "--" + prefix_str + "nbnetwork.network",
                default=default_network,
                type=str,
                help="""The nbnetwork network flag. If set, overrides the --network flag.
                                    """,
            )

            parser.add_argument(
                "--" + prefix_str + "nbnetwork.chain_endpoint",
                default=default_chain_endpoint,
                type=str,
                help="""The nbnetwork endpoint flag. If set, overrides the --network flag.
                                    """,
            )

        except argparse.ArgumentError:
            # re-parsing arguments.
            pass

    @staticmethod
    def determine_chain_endpoint_and_network(network: str):
        """Determines the chain endpoint and network from the passed network or chain_endpoint.
        Args:
            network (str): The network flag. The likely choices are:
                    -- nimble (main network)
                    -- archive (archive network +300 blocks)
                    -- local (local running network)
                    -- test (test network)
            chain_endpoint (str): The chain endpoint flag. If set, overrides the network argument.
        Returns:
            network (str): The network flag. The likely choices are:
            chain_endpoint (str): The chain endpoint flag. If set, overrides the network argument.
        """
        if network == None:
            return None, None
        if network in ["nimble", "local", "test", "archive"]:
            if network == "nimble":
                # Kiru nimble stagin network.
                return network, nimlib.__nimble_entrypoint__
            elif network == "local":
                return network, nimlib.__local_entrypoint__
            elif network == "test":
                return network, nimlib.__nimble_test_entrypoint__
            elif network == "archive":
                return network, nimlib.__archive_entrypoint__
        else:
            if (
                network == nimlib.__nimble_entrypoint__
                or "entrypoint-nimlib.nimble-technology.ai" in network
            ):
                return "nimble", nimlib.__nimble_entrypoint__
            elif (
                network == nimlib.__nimble_test_entrypoint__
                or "test.nimlib.nimble-technology.ai" in network
            ):
                return "test", nimlib.__nimble_test_entrypoint__
            elif (
                network == nimlib.__archive_entrypoint__
                or "archive.chain.nimble-technology.ai" in network
            ):
                return "archive", nimlib.__archive_entrypoint__
            elif "127.0.0.1" in network or "localhost" in network:
                return "local", network
            else:
                return "unknown", network

    @staticmethod
    def setup_config(network: str, config: nimlib.config):
        if network != None:
            (
                evaluated_network,
                evaluated_endpoint,
            ) = NimbleNetwork.determine_chain_endpoint_and_network(network)
        else:
            if config.get("__is_set", {}).get("nbnetwork.chain_endpoint"):
                (
                    evaluated_network,
                    evaluated_endpoint,
                ) = NimbleNetwork.determine_chain_endpoint_and_network(
                    config.nbnetwork.chain_endpoint
                )

            elif config.get("__is_set", {}).get("nbnetwork.network"):
                (
                    evaluated_network,
                    evaluated_endpoint,
                ) = NimbleNetwork.determine_chain_endpoint_and_network(
                    config.nbnetwork.network
                )

            elif config.nbnetwork.get("chain_endpoint"):
                (
                    evaluated_network,
                    evaluated_endpoint,
                ) = NimbleNetwork.determine_chain_endpoint_and_network(
                    config.nbnetwork.chain_endpoint
                )

            elif config.nbnetwork.get("network"):
                (
                    evaluated_network,
                    evaluated_endpoint,
                ) = NimbleNetwork.determine_chain_endpoint_and_network(
                    config.nbnetwork.network
                )

            else:
                (
                    evaluated_network,
                    evaluated_endpoint,
                ) = NimbleNetwork.determine_chain_endpoint_and_network(
                    nimlib.defaults.nbnetwork.network
                )

        return (
            nimlib.utils.networking.get_formatted_ws_endpoint_url(
                evaluated_endpoint
            ),
            evaluated_network,
        )

    def __init__(
        self,
        network: str = None,
        config: "nimlib.config" = None,
        _mock: bool = False,
        log_verbose: bool = True,
    ) -> None:
        """
        Initializes a NbNetwork interface for interacting with the nimble blockchain.

        NOTE: Currently nbnetwork defaults to the nimble network. This will change in a future release.

        We strongly encourage users to run their own local nbnetwork node whenever possible. This increases
        decentralization and resilience of the network. In a future release, local nbnetwork will become the
        default and the fallback to nimble removed. Please plan ahead for this change. We will provide detailed
        instructions on how to run a local nbnetwork node in the documentation in a subsequent release.

        Args:
            network (str, optional): The network name to connect to (e.g., 'nimble', 'local').
                                     Defaults to the main nimble network if not specified.
            config (nimlib.config, optional): Configuration object for the nbnetwork.
                                                 If not provided, a default configuration is used.
            _mock (bool, optional): If set to True, uses a mocked connection for testing purposes.

        This initialization sets up the connection to the specified nimble network, allowing for various
        blockchain operations such as particle registration, stake management, and setting weights.

        """
        # Determine config.nbnetwork.chain_endpoint and config.nbnetwork.network config.
        # If chain_endpoint is set, we override the network flag, otherwise, the chain_endpoint is assigned by the network.
        # Argument importance: network > chain_endpoint > config.nbnetwork.chain_endpoint > config.nbnetwork.network
        if config == None:
            config = NimbleNetwork.config()
        self.config = copy.deepcopy(config)

        # Setup config.nbnetwork.network and config.nbnetwork.chain_endpoint
        self.chain_endpoint, self.network = NimbleNetwork.setup_config(
            network, config
        )

        if (
            self.network == "nimble"
            or self.chain_endpoint == nimlib.__nimble_entrypoint__
        ) and log_verbose:
            nimlib.logging.info(
                f"You are connecting to {self.network} network with endpoint {self.chain_endpoint}."
            )
            nimlib.logging.warning(
                "We strongly encourage running a local nbnetwork node whenever possible. "
                "This increases decentralization and resilience of the network."
            )
            nimlib.logging.warning(
                "In a future release, local nbnetwork will become the default endpoint. "
                "To get ahead of this change, please run a local nbnetwork node and point to it."
            )

        # Returns a mocked connection with a background chain connection.
        self.config.nbnetwork._mock = (
            _mock
            if _mock != None
            else self.config.nbnetwork.get(
                "_mock", nimlib.defaults.nbnetwork._mock
            )
        )
        if self.config.nbnetwork._mock:
            config.nbnetwork._mock = True
            return nimlib.nbnetwork_mock.MockNbNetwork()

        # Attempt to connect to chosen endpoint. Fallback to nimble if local unavailable.
        try:
            # Set up params.
            self.substrate = SubstrateInterface(
                ss58_format=nimlib.__ss58_format__,
                use_remote_preset=True,
                url=self.chain_endpoint,
                type_registry=nimlib.__type_registry__,
            )
        except ConnectionRefusedError as e:
            nimlib.logging.error(
                f"Could not connect to {self.network} network with {self.chain_endpoint} chain endpoint. Exiting..."
            )
            nimlib.logging.info(
                f"You can check if you have connectivity by runing this command: nc -vz localhost {self.chain_endpoint.split(':')[2]}"
            )
            exit(1)
            # TODO (edu/phil): Advise to run local nbnetwork and point to dev docs.

        try:
            self.substrate.websocket.settimeout(600)
        except:
            nimlib.logging.warning("Could not set websocket timeout.")

        if log_verbose:
            nimlib.logging.info(
                f"Connected to {self.network} network and {self.chain_endpoint}."
            )

    def __str__(self) -> str:
        if self.network == self.chain_endpoint:
            # Connecting to chain endpoint without network known.
            return "nbnetwork({})".format(self.chain_endpoint)
        else:
            # Connecting to network with endpoint known.
            return "nbnetwork({}, {})".format(self.network, self.chain_endpoint)

    def __repr__(self) -> str:
        return self.__str__()

    ######################
    #### Registration ####
    ######################
    def register(
        self,
        wallet: "nimlib.wallet",
        netuid: int,
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
        prompt: bool = False,
        max_allowed_attempts: int = 3,
        output_in_place: bool = True,
        cuda: bool = False,
        dev_id: Union[List[int], int] = 0,
        tpb: int = 256,
        num_processes: Optional[int] = None,
        update_interval: Optional[int] = None,
        log_verbose: bool = False,
    ) -> bool:
        """
        Registers a neuron on the nimble network using the provided wallet. Registration
        is a critical step for a neuron to become an active participant in the network, enabling
        it to stake, set weights, and receive incentives.

        Args:
            wallet (nimlib.wallet): The wallet associated with the neuron to be registered.
            netuid (int): The unique identifier of the subnet.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            Other arguments: Various optional parameters to customize the registration process.

        Returns:
            bool: True if the registration is successful, False otherwise.

        This function facilitates the entry of new neurons into the network, supporting the decentralized
        growth and scalability of the nimble ecosystem.
        """
        return register_extrinsic(
            nbnetwork=self,
            wallet=wallet,
            netuid=netuid,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
            prompt=prompt,
            max_allowed_attempts=max_allowed_attempts,
            output_in_place=output_in_place,
            cuda=cuda,
            dev_id=dev_id,
            tpb=tpb,
            num_processes=num_processes,
            update_interval=update_interval,
            log_verbose=log_verbose,
        )

    def burned_register(
        self,
        wallet: "nimlib.wallet",
        netuid: int,
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
        prompt: bool = False,
    ) -> bool:
        """
        Registers a neuron on the nimble network by burning NIM. This method of registration
        involves recycling NIM tokens, contributing to the network's deflationary mechanism.

        Args:
            wallet (nimlib.wallet): The wallet associated with the neuron to be registered.
            netuid (int): The unique identifier of the subnet.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            prompt (bool, optional): If True, prompts for user confirmation before proceeding.

        Returns:
            bool: True if the registration is successful, False otherwise.

        This function offers an alternative registration path, aligning with the network's principles
        of token circulation and value conservation.
        """
        return burned_register_extrinsic(
            nbnetwork=self,
            wallet=wallet,
            netuid=netuid,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
            prompt=prompt,
        )

    def _do_burned_register(
        self,
        netuid: int,
        wallet: "nimlib.wallet",
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                # create extrinsic call
                call = substrate.compose_call(
                    call_module="NbNetworkModule",
                    call_function="burned_register",
                    call_params={
                        "netuid": netuid,
                        "hotkey": wallet.hotkey.ss58_address,
                    },
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

                # process if registration successful, try again if pow is still valid
                response.process_events()
                if not response.is_success:
                    return False, response.error_message
                # Successful registration
                else:
                    return True, None

        return make_substrate_call_with_retry()

    ##################
    #### Transfer ####
    ##################
    def transfer(
        self,
        wallet: "nimlib.wallet",
        dest: str,
        amount: Union[Balance, float],
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
        predict: bool = False,
    ) -> bool:
        """
        Executes a transfer of funds from the provided wallet to the specified destination address.
        This function is used to move NIM tokens within the nimble network, facilitating transactions
        between particles.

        Args:
            wallet (nimlib.wallet): The wallet from which funds are being transferred.
            dest (str): The destination public key address.
            amount (Union[Balance, float]): The amount of NIM to be transferred.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            predict (bool, optional): If True, inferences or predictions for user confirmation before proceeding.

        Returns:
            bool: True if the transfer is successful, False otherwise.

        This function is essential for the fluid movement of tokens in the network, supporting
        various economic activities such as staking, delegation, and reward distribution.
        """
        return transfer_extrinsic(
            nbnetwork=self,
            wallet=wallet,
            dest=dest,
            amount=amount,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
            predict=predict,
        )

    def get_transfer_fee(
        self,
        wallet: "nimlib.wallet",
        dest: str,
        value: Union[Balance, float, int],
    ) -> Balance:
        """
        Calculates the transaction fee for transferring tokens from a wallet to a specified destination address.
        This function simulates the transfer to estimate the associated cost, taking into account the current
        network conditions and transaction complexity.

        Args:
            wallet (nimlib.wallet): The wallet from which the transfer is initiated.
            dest (str): The SS58 address of the destination account.
            value (Union[Balance, float, int]): The amount of tokens to be transferred, specified as a Balance object,
                                                or in Nim (float) or Vim (int) units.

        Returns:
            Balance: The estimated transaction fee for the transfer, represented as a Balance object.

        Estimating the transfer fee is essential for planning and executing token transactions, ensuring that the
        wallet has sufficient funds to cover both the transfer amount and the associated costs. This function
        provides a crucial tool for managing financial operations within the nimble network.
        """
        if isinstance(value, float):
            transfer_balance = Balance.from_nim(value)
        elif isinstance(value, int):
            transfer_balance = Balance.from_vim(value)

        with self.substrate as substrate:
            call = substrate.compose_call(
                call_module="Balances",
                call_function="transfer",
                call_params={"dest": dest, "value": transfer_balance.vim},
            )

            try:
                payment_info = substrate.get_payment_info(
                    call=call, keypair=wallet.coldkeypub
                )
            except Exception as e:
                nimlib.__console__.print(
                    ":cross_mark: [red]Failed to get payment info[/red]:[bold white]\n  {}[/bold white]".format(
                        e
                    )
                )
                payment_info = {"partialFee": 2e7}  # assume  0.02 Nim

        fee = Balance.from_vim(payment_info["partialFee"])
        return fee

    def _do_transfer(
        self,
        wallet: "nimlib.wallet",
        dest: str,
        transfer_balance: Balance,
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Sends a transfer extrinsic to the chain.
        Args:
            wallet (:obj:`nimlib.wallet`): Wallet object.
            dest (:obj:`str`): Destination public key address.
            transfer_balance (:obj:`Balance`): Amount to transfer.
            wait_for_inclusion (:obj:`bool`): If true, waits for inclusion.
            wait_for_finalization (:obj:`bool`): If true, waits for finalization.
        Returns:
            success (:obj:`bool`): True if transfer was successful.
            block_hash (:obj:`str`): Block hash of the transfer.
                (On success and if wait_for_ finalization/inclusion is True)
            error (:obj:`str`): Error message if transfer failed.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                call = substrate.compose_call(
                    call_module="Balances",
                    call_function="transfer",
                    call_params={"dest": dest, "value": transfer_balance.vim},
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
                    return True, None, None

                # Otherwise continue with finalization.
                response.process_events()
                if response.is_success:
                    block_hash = response.block_hash
                    return True, block_hash, None
                else:
                    return False, None, response.error_message

        return make_substrate_call_with_retry()

    def get_existential_deposit(
        self, block: Optional[int] = None
    ) -> Optional[Balance]:
        """
        Retrieves the existential deposit amount for the nimble blockchain. The existential deposit
        is the minimum amount of NIM required for an account to exist on the blockchain. Accounts with
        balances below this threshold can be reaped to conserve network resources.

        Args:
            block (Optional[int], optional): Block number at which to query the deposit amount. If None,
                                            the current block is used.

        Returns:
            Optional[Balance]: The existential deposit amount, or None if the query fails.

        The existential deposit is a fundamental economic parameter in the nimble network, ensuring
        efficient use of storage and preventing the proliferation of dust accounts.
        """
        result = self.query_constant(
            module_name="Balances",
            constant_name="ExistentialDeposit",
            block=block,
        )

        if result is None:
            return None

        return Balance.from_vim(result.value)

    #################
    #### Serving ####
    #################
    def serve(
        self,
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
        """
        Registers a particle's serving endpoint on the nimble network. This function announces the
        IP address and port where the particle is available to serve requests, facilitating peer-to-peer
        communication within the network.

        Args:
            wallet (nimlib.wallet): The wallet associated with the particle being served.
            ip (str): The IP address of the serving particle.
            port (int): The port number on which the particle is serving.
            protocol (int): The protocol type used by the particle (e.g., GRPC, HTTP).
            netuid (int): The unique identifier of the cosmos.
            Other arguments: Placeholder parameters for future extensions.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            predict (bool, optional): If True, inferences for user confirmation before proceeding.

        Returns:
            bool: True if the serve registration is successful, False otherwise.

        This function is essential for establishing the particle's presence in the network, enabling
        it to participate in the decentralized machine learning processes of nimble.
        """
        return serve_extrinsic(
            self,
            wallet,
            ip,
            port,
            protocol,
            netuid,
            placeholder1,
            placeholder2,
            wait_for_inclusion,
            wait_for_finalization,
        )

    def serve_fermion(
        self,
        netuid: int,
        fermion: "nimlib.Fermion",
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
        predict: bool = False,
    ) -> bool:
        """
        Registers an Fermion serving endpoint on the nimble network for a specific particle. This function
        is used to set up the Fermion, a key component of a particle that handles incoming queries and data
        processing tasks.

        Args:
            netuid (int): The unique identifier of the cosmos.
            fermion (nimlib.Fermion): The Fermion instance to be registered for serving.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            predict (bool, optional): If True, inferences for user confirmation before proceeding.

        Returns:
            bool: True if the Fermion serve registration is successful, False otherwise.

        By registering an Fermion, the particle becomes an active part of the network's distributed
        computing infrastructure, contributing to the collective intelligence of nimble.
        """
        return serve_fermion_extrinsic(
            self, netuid, fermion, wait_for_inclusion, wait_for_finalization
        )

    def _do_serve_fermion(
        self,
        wallet: "nimlib.wallet",
        call_params: FermionServeCallParams,
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Internal method to submit a serve fermion transaction to the nimble blockchain. This method
        creates and submits a transaction, enabling a particle's Fermion to serve requests on the network.

        Args:
            wallet (nimlib.wallet): The wallet associated with the particle.
            call_params (FermionServeCallParams): Parameters required for the serve fermion call.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.

        Returns:
            Tuple[bool, Optional[str]]: A tuple containing a success flag and an optional error message.

        This function is crucial for initializing and announcing a particle's Fermion service on the network,
        enhancing the decentralized computation capabilities of nimble.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                call = substrate.compose_call(
                    call_module="NbNetworkModule",
                    call_function="serve_fermion",
                    call_params=call_params,
                )
                extrinsic = substrate.create_signed_extrinsic(
                    call=call, keypair=wallet.hotkey
                )
                response = substrate.submit_extrinsic(
                    extrinsic,
                    wait_for_inclusion=wait_for_inclusion,
                    wait_for_finalization=wait_for_finalization,
                )
                if wait_for_inclusion or wait_for_finalization:
                    response.process_events()
                    if response.is_success:
                        return True, None
                    else:
                        return False, response.error_message
                else:
                    return True, None

        return make_substrate_call_with_retry()

    def _do_associate_ips(
        self,
        wallet: "nimlib.wallet",
        ip_info_list: List[IPInfo],
        netuid: int,
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Sends an associate IPs extrinsic to the chain.

        Args:
            wallet (:obj:`nimlib.wallet`): Wallet object.
            ip_info_list (:obj:`List[IPInfo]`): List of IPInfo objects.
            netuid (:obj:`int`): Netuid to associate IPs to.
            wait_for_inclusion (:obj:`bool`): If true, waits for inclusion.
            wait_for_finalization (:obj:`bool`): If true, waits for finalization.

        Returns:
            success (:obj:`bool`): True if associate IPs was successful.
            error (:obj:`Optional[str]`): Error message if associate IPs failed, None otherwise.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                call = substrate.compose_call(
                    call_module="NbNetworkModule",
                    call_function="associate_ips",
                    call_params={
                        "ip_info_list": [
                            ip_info.encode() for ip_info in ip_info_list
                        ],
                        "netuid": netuid,
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
                if wait_for_inclusion or wait_for_finalization:
                    response.process_events()
                    if response.is_success:
                        return True, None
                    else:
                        return False, response.error_message
                else:
                    return True, None

        return make_substrate_call_with_retry()

    #################
    #### Staking ####
    #################
    def add_stake(
        self,
        wallet: "nimlib.wallet",
        hotkey_ss58: Optional[str] = None,
        amount: Union[Balance, float] = None,
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
        predict: bool = False,
    ) -> bool:
        """
        Adds the specified amount of stake to a particle identified by the hotkey SS58 address. Staking
        is a fundamental process in the nimble network that enables particles to participate actively
        and earn incentives.

        Args:
            wallet (nimlib.wallet): The wallet to be used for staking.
            hotkey_ss58 (Optional[str]): The SS58 address of the hotkey associated with the particle.
            amount (Union[Balance, float]): The amount of NIM to stake.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            predict (bool, optional): If True, inferences for user confirmation before proceeding.

        Returns:
            bool: True if the staking is successful, False otherwise.

        This function enables particles to increase their stake in the network, enhancing their influence
        and potential rewards in line with nimble's consensus and reward mechanisms.
        """
        return add_stake_extrinsic(
            nbnetwork=self,
            wallet=wallet,
            hotkey_ss58=hotkey_ss58,
            amount=amount,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
            predict=predict,
        )

    def add_stake_multiple(
        self,
        wallet: "nimlib.wallet",
        hotkey_ss58s: List[str],
        amounts: List[Union[Balance, float]] = None,
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
        predict: bool = False,
    ) -> bool:
        """
        Adds stakes to multiple particles identified by their hotkey SS58 addresses. This bulk operation
        allows for efficient staking across different particles from a single wallet.

        Args:
            wallet (nimlib.wallet): The wallet used for staking.
            hotkey_ss58s (List[str]): List of SS58 addresses of hotkeys to stake to.
            amounts (List[Union[Balance, float]], optional): Corresponding amounts of NIM to stake for each hotkey.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            predict (bool, optional): If True, inferences for user confirmation before proceeding.

        Returns:
            bool: True if the staking is successful for all specified particles, False otherwise.

        This function is essential for managing stakes across multiple particles, reflecting the dynamic
        and collaborative nature of the nimble network.
        """
        return add_stake_multiple_extrinsic(
            self,
            wallet,
            hotkey_ss58s,
            amounts,
            wait_for_inclusion,
            wait_for_finalization,
            predict,
        )

    def _do_stake(
        self,
        wallet: "nimlib.wallet",
        hotkey_ss58: str,
        amount: Balance,
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> bool:
        """Sends a stake extrinsic to the chain.
        Args:
            wallet (:obj:`nimlib.wallet`): Wallet object that can sign the extrinsic.
            hotkey_ss58 (:obj:`str`): Hotkey ss58 address to stake to.
            amount (:obj:`Balance`): Amount to stake.
            wait_for_inclusion (:obj:`bool`): If true, waits for inclusion before returning.
            wait_for_finalization (:obj:`bool`): If true, waits for finalization before returning.
        Returns:
            success (:obj:`bool`): True if the extrinsic was successful.
        Raises:
            StakeError: If the extrinsic failed.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                call = substrate.compose_call(
                    call_module="NbNetworkModule",
                    call_function="add_stake",
                    call_params={
                        "hotkey": hotkey_ss58,
                        "amount_staked": amount.vim,
                    },
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

                response.process_events()
                if response.is_success:
                    return True
                else:
                    raise StakeError(response.error_message)

        return make_substrate_call_with_retry()

    ###################
    #### Unstaking ####
    ###################
    def unstake_multiple(
        self,
        wallet: "nimlib.wallet",
        hotkey_ss58s: List[str],
        amounts: List[Union[Balance, float]] = None,
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
        predict: bool = False,
    ) -> bool:
        """
        Performs batch unstaking from multiple hotkey accounts, allowing a particle to reduce its staked amounts
        efficiently. This function is useful for managing the distribution of stakes across multiple particles.

        Args:
            wallet (nimlib.wallet): The wallet linked to the coldkey from which the stakes are being withdrawn.
            hotkey_ss58s (List[str]): A list of hotkey SS58 addresses to unstake from.
            amounts (List[Union[Balance, float]], optional): The amounts of NIM to unstake from each hotkey.
                                                            If not provided, unstakes all available stakes.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            predict (bool, optional): If True, inferences for user confirmation before proceeding.

        Returns:
            bool: True if the batch unstaking is successful, False otherwise.

        This function allows for strategic reallocation or withdrawal of stakes, aligning with the dynamic
        stake management aspect of the nimble network.
        """
        return unstake_multiple_extrinsic(
            self,
            wallet,
            hotkey_ss58s,
            amounts,
            wait_for_inclusion,
            wait_for_finalization,
            predict,
        )

    def unstake(
        self,
        wallet: "nimlib.wallet",
        hotkey_ss58: Optional[str] = None,
        amount: Union[Balance, float] = None,
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
        predict: bool = False,
    ) -> bool:
        """
        Removes a specified amount of stake from a single hotkey account. This function is critical for adjusting
        individual particle stakes within the nimble network.

        Args:
            wallet (nimlib.wallet): The wallet associated with the particle from which the stake is being removed.
            hotkey_ss58 (Optional[str]): The SS58 address of the hotkey account to unstake from.
            amount (Union[Balance, float], optional): The amount of NIM to unstake. If not specified, unstakes all.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.
            predict (bool, optional): If True, inference for user confirmation before proceeding.

        Returns:
            bool: True if the unstaking process is successful, False otherwise.

        This function supports flexible stake management, allowing particles to adjust their network participation
        and potential reward accruals.
        """
        return unstake_extrinsic(
            self,
            wallet,
            hotkey_ss58,
            amount,
            wait_for_inclusion,
            wait_for_finalization,
            predict,
        )

    def _do_unstake(
        self,
        wallet: "nimlib.wallet",
        hotkey_ss58: str,
        amount: Balance,
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> bool:
        """Sends an unstake extrinsic to the chain.
        Args:
            wallet (:obj:`nimlib.wallet`): Wallet object that can sign the extrinsic.
            hotkey_ss58 (:obj:`str`): Hotkey ss58 address to unstake from.
            amount (:obj:`Balance`): Amount to unstake.
            wait_for_inclusion (:obj:`bool`): If true, waits for inclusion before returning.
            wait_for_finalization (:obj:`bool`): If true, waits for finalization before returning.
        Returns:
            success (:obj:`bool`): True if the extrinsic was successful.
        Raises:
            StakeError: If the extrinsic failed.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                call = substrate.compose_call(
                    call_module="NbNetworkModule",
                    call_function="remove_stake",
                    call_params={
                        "hotkey": hotkey_ss58,
                        "amount_unstaked": amount.vim,
                    },
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

                response.process_events()
                if response.is_success:
                    return True
                else:
                    raise StakeError(response.error_message)

        return make_substrate_call_with_retry()

    """ Queries nbnetwork registry named storage with params and block. """

    def query_identity(
        self,
        key: str,
        block: Optional[int] = None,
    ) -> Optional[object]:
        """
        Queries the identity of a particle on the nimble blockchain using the given key. This function retrieves
        detailed identity information about a specific particle, which is a crucial aspect of the network's decentralized
        identity and governance system.

        NOTE: See the nimble cli documentation for supported identity parameters.

        Args:
            key (str): The key used to query the particle's identity, typically the particle's SS58 address.
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            Optional[object]: An object containing the identity information of the particle if found, None otherwise.

        The identity information can include various attributes such as the particle's stake, rank, and other
        network-specific details, providing insights into the particle's role and status within the nimble network.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                return substrate.query(
                    module="Registry",
                    storage_function="IdentityOf",
                    params=[key],
                    block_hash=None
                    if block == None
                    else substrate.get_block_hash(block),
                )

        identity_info = make_substrate_call_with_retry()
        return nimlib.utils.wallet_utils.decode_hex_identity_dict(
            identity_info.value["info"]
        )

    def update_identity(
        self,
        wallet: "nimlib.wallet",
        identified: str = None,
        params: dict = {},
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> bool:
        """
        Updates the identity of a particle on the nimble blockchain. This function allows particles to modify their
        identity attributes, reflecting changes in their roles, stakes, or other network-specific parameters.

        NOTE: See the nimble cli documentation for supported identity parameters.

        Args:
            wallet (nimlib.wallet): The wallet associated with the particle whose identity is being updated.
            identified (str, optional): The identified SS58 address of the particle. Defaults to the wallet's coldkey address.
            params (dict, optional): A dictionary of parameters to update in the particle's identity.
            wait_for_inclusion (bool, optional): Waits for the transaction to be included in a block.
            wait_for_finalization (bool, optional): Waits for the transaction to be finalized on the blockchain.

        Returns:
            bool: True if the identity update is successful, False otherwise.

        This function plays a vital role in maintaining the accuracy and currency of particle identities in the
        nimble network, ensuring that the network's governance and consensus mechanisms operate effectively.
        """
        if identified == None:
            identified = wallet.coldkey.ss58_address

        call_params = nimlib.utils.wallet_utils.create_identity_dict(**params)
        call_params["identified"] = identified

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                call = substrate.compose_call(
                    call_module="Registry",
                    call_function="set_identity",
                    call_params=call_params,
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
                response.process_events()
                if response.is_success:
                    return True
                else:
                    raise IdentityError(response.error_message)

        return make_substrate_call_with_retry()

    ########################
    #### Standard Calls ####
    ########################

    """ Queries nbnetwork named storage with params and block. """

    def query_nbnetwork(
        self,
        name: str,
        block: Optional[int] = None,
        params: Optional[List[object]] = [],
    ) -> Optional[object]:
        """
        Queries named storage from the NbNetwork module on the nimble blockchain. This function is used to retrieve
        specific data or parameters from the blockchain, such as stake, rank, or other particle-specific attributes.

        Args:
            name (str): The name of the storage function to query.
            block (Optional[int], optional): The blockchain block number at which to perform the query.
            params (Optional[List[object]], optional): A list of parameters to pass to the query function.

        Returns:
            Optional[object]: An object containing the requested data if found, None otherwise.

        This query function is essential for accessing detailed information about the network and its particles,
        providing valuable insights into the state and dynamics of the nimble ecosystem.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                return substrate.query(
                    module="NbNetworkModule",
                    storage_function=name,
                    params=params,
                    block_hash=None
                    if block == None
                    else substrate.get_block_hash(block),
                )

        return make_substrate_call_with_retry()

    """ Queries nbnetwork map storage with params and block. """

    def query_map_nbnetwork(
        self,
        name: str,
        block: Optional[int] = None,
        params: Optional[List[object]] = [],
    ) -> QueryMapResult:
        """
        Queries map storage from the NbNetwork module on the nimble blockchain. This function is designed to
        retrieve a map-like data structure, which can include various particle-specific details or network-wide attributes.

        Args:
            name (str): The name of the map storage function to query.
            block (Optional[int], optional): The blockchain block number at which to perform the query.
            params (Optional[List[object]], optional): A list of parameters to pass to the query function.

        Returns:
            QueryMapResult: An object containing the map-like data structure, or None if not found.

        This function is particularly useful for analyzing and understanding complex network structures and
        relationships within the nimble ecosystem, such as inter-particle connections and stake distributions.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                return substrate.query_map(
                    module="NbNetworkModule",
                    storage_function=name,
                    params=params,
                    block_hash=None
                    if block == None
                    else substrate.get_block_hash(block),
                )

        return make_substrate_call_with_retry()

    def query_constant(
        self, module_name: str, constant_name: str, block: Optional[int] = None
    ) -> Optional[object]:
        """
        Retrieves a constant from the specified module on the nimble blockchain. This function is used to
        access fixed parameters or values defined within the blockchain's modules, which are essential for
        understanding the network's configuration and rules.

        Args:
            module_name (str): The name of the module containing the constant.
            constant_name (str): The name of the constant to retrieve.
            block (Optional[int], optional): The blockchain block number at which to query the constant.

        Returns:
            Optional[object]: The value of the constant if found, None otherwise.

        Constants queried through this function can include critical network parameters such as inflation rates,
        consensus rules, or validation thresholds, providing a deeper understanding of the nimble network's
        operational parameters.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                return substrate.get_constant(
                    module_name=module_name,
                    constant_name=constant_name,
                    block_hash=None
                    if block == None
                    else substrate.get_block_hash(block),
                )

        return make_substrate_call_with_retry()

    """ Queries any module storage with params and block. """

    def query_module(
        self,
        module: str,
        name: str,
        block: Optional[int] = None,
        params: Optional[List[object]] = [],
    ) -> Optional[object]:
        """
        Queries any module storage on the nimble blockchain with the specified parameters and block number.
        This function is a generic query interface that allows for flexible and diverse data retrieval from
        various blockchain modules.

        Args:
            module (str): The name of the module from which to query data.
            name (str): The name of the storage function within the module.
            block (Optional[int], optional): The blockchain block number at which to perform the query.
            params (Optional[List[object]], optional): A list of parameters to pass to the query function.

        Returns:
            Optional[object]: An object containing the requested data if found, None otherwise.

        This versatile query function is key to accessing a wide range of data and insights from different
        parts of the nimble blockchain, enhancing the understanding and analysis of the network's state and dynamics.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                return substrate.query(
                    module=module,
                    storage_function=name,
                    params=params,
                    block_hash=None
                    if block == None
                    else substrate.get_block_hash(block),
                )

        return make_substrate_call_with_retry()

    """ Queries any module map storage with params and block. """

    def query_map(
        self,
        module: str,
        name: str,
        block: Optional[int] = None,
        params: Optional[List[object]] = [],
    ) -> Optional[object]:
        """
        Queries map storage from any module on the nimble blockchain. This function retrieves data structures
        that represent key-value mappings, essential for accessing complex and structured data within the blockchain modules.

        Args:
            module (str): The name of the module from which to query the map storage.
            name (str): The specific storage function within the module to query.
            block (Optional[int], optional): The blockchain block number at which to perform the query.
            params (Optional[List[object]], optional): Parameters to be passed to the query.

        Returns:
            Optional[object]: A data structure representing the map storage if found, None otherwise.

        This function is particularly useful for retrieving detailed and structured data from various blockchain
        modules, offering insights into the network's state and the relationships between its different components.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                return substrate.query_map(
                    module=module,
                    storage_function=name,
                    params=params,
                    block_hash=None
                    if block == None
                    else substrate.get_block_hash(block),
                )

        return make_substrate_call_with_retry()

    def state_call(
        self,
        method: str,
        data: str,
        block: Optional[int] = None,
    ) -> Optional[object]:
        """
        Makes a state call to the nimble blockchain, allowing for direct queries of the blockchain's state.
        This function is typically used for advanced queries that require specific method calls and data inputs.

        Args:
            method (str): The method name for the state call.
            data (str): The data to be passed to the method.
            block (Optional[int], optional): The blockchain block number at which to perform the state call.

        Returns:
            Optional[object]: The result of the state call if successful, None otherwise.

        The state call function provides a more direct and flexible way of querying blockchain data,
        useful for specific use cases where standard queries are insufficient.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                block_hash = (
                    None if block == None else substrate.get_block_hash(block)
                )
                params = [method, data]
                if block_hash:
                    params = params + [block_hash]
                return substrate.rpc_request(method="state_call", params=params)

        return make_substrate_call_with_retry()

    def query_runtime_api(
        self,
        runtime_api: str,
        method: str,
        params: Optional[List[ParamWithTypes]],
        block: Optional[int] = None,
    ) -> Optional[bytes]:
        """
        Queries the runtime API of the nimble blockchain, providing a way to interact with the underlying
        runtime and retrieve data encoded in Scale Bytes format. This function is essential for advanced users
        who need to interact with specific runtime methods and decode complex data types.

        Args:
            runtime_api (str): The name of the runtime API to query.
            method (str): The specific method within the runtime API to call.
            params (Optional[List[ParamWithTypes]], optional): The parameters to pass to the method call.
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            Optional[bytes]: The Scale Bytes encoded result from the runtime API call, or None if the call fails.

        This function enables access to the deeper layers of the nimble blockchain, allowing for detailed
        and specific interactions with the network's runtime environment.
        """
        call_definition = nimlib.__type_registry__["runtime_api"][runtime_api][
            "methods"
        ][method]

        json_result = self.state_call(
            method=f"{runtime_api}_{method}",
            data="0x"
            if params is None
            else self._encode_params(
                call_definition=call_definition, params=params
            ),
            block=block,
        )

        if json_result is None:
            return None

        return_type = call_definition["type"]

        as_scale_bytes = scalecodec.ScaleBytes(json_result["result"])

        rpc_runtime_config = RuntimeConfiguration()
        rpc_runtime_config.update_type_registry(
            load_type_registry_preset("legacy")
        )
        rpc_runtime_config.update_type_registry(custom_rpc_type_registry)

        obj = rpc_runtime_config.create_scale_object(
            return_type, as_scale_bytes
        )
        if obj.data.to_hex() == "0x0400":  # RPC returned None result
            return None

        return obj.decode()

    def _encode_params(
        self,
        call_definition: List[ParamWithTypes],
        params: Union[List[Any], Dict[str, str]],
    ) -> str:
        """
        Returns a hex encoded string of the params using their types.
        """
        param_data = scalecodec.ScaleBytes(b"")

        for i, param in enumerate(call_definition["params"]):
            scale_obj = self.substrate.create_scale_object(param["type"])
            if type(params) is list:
                param_data += scale_obj.encode(params[i])
            else:
                if param["name"] not in params:
                    raise ValueError(
                        f"Missing param {param['name']} in params dict."
                    )

                param_data += scale_obj.encode(params[param["name"]])

        return param_data.to_hex()

    #####################################
    #### Hyper parameter calls. ####
    #####################################

    def tempo(self, netuid: int, block: Optional[int] = None) -> int:
        """Returns network Tempo hyper parameter"""
        if not self.cosmos_exists(netuid, block):
            return None
        return self.query_nbnetwork("Tempo", block, [netuid]).value

    ##########################
    #### Account functions ###
    ##########################

    def get_total_stake_for_hotkey(
        self, ss58_address: str, block: Optional[int] = None
    ) -> Optional["Balance"]:
        """Returns the total stake held on a hotkey including delegative"""
        return Balance.from_vim(
            self.query_nbnetwork(
                "TotalHotkeyStake", block, [ss58_address]
            ).value
        )

    def get_total_stake_for_coldkey(
        self, ss58_address: str, block: Optional[int] = None
    ) -> Optional["Balance"]:
        """Returns the total stake held on a coldkey across all hotkeys including delegates"""
        return Balance.from_vim(
            self.query_nbnetwork(
                "TotalColdkeyStake", block, [ss58_address]
            ).value
        )

    def get_stake_for_coldkey_and_hotkey(
        self, hotkey_ss58: str, coldkey_ss58: str, block: Optional[int] = None
    ) -> Optional["Balance"]:
        """Returns the stake under a coldkey - hotkey pairing"""
        return Balance.from_vim(
            self.query_nbnetwork(
                "Stake", block, [hotkey_ss58, coldkey_ss58]
            ).value
        )

    def get_stake(
        self, hotkey_ss58: str, block: Optional[int] = None
    ) -> List[Tuple[str, "Balance"]]:
        """Returns a list of stake tuples (coldkey, balance) for each delegating coldkey including the owner"""
        return [
            (r[0].value, Balance.from_vim(r[1].value))
            for r in self.query_map_nbnetwork("Stake", block, [hotkey_ss58])
        ]

    def does_hotkey_exist(
        self, hotkey_ss58: str, block: Optional[int] = None
    ) -> bool:
        """Returns true if the hotkey is known by the chain and there are accounts."""
        return (
            self.query_nbnetwork("Owner", block, [hotkey_ss58]).value
            != "5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1eSuyUpnhM"
        )

    def get_hotkey_owner(
        self, hotkey_ss58: str, block: Optional[int] = None
    ) -> Optional[str]:
        """Returns the coldkey owner of the passed hotkey"""
        if self.does_hotkey_exist(hotkey_ss58, block):
            return self.query_nbnetwork("Owner", block, [hotkey_ss58]).value
        else:
            return None

    def get_fermion_info(
        self, netuid: int, hotkey_ss58: str, block: Optional[int] = None
    ) -> Optional[FermionInfo]:
        """Returns the fermion information for this hotkey account"""
        result = self.query_nbnetwork("Fermions", block, [netuid, hotkey_ss58])
        if result != None:
            return FermionInfo(
                ip=nimlib.utils.networking.int_to_ip(result.value["ip"]),
                ip_type=result.value["ip_type"],
                port=result.value["port"],
                protocol=result.value["protocol"],
                version=result.value["version"],
                placeholder1=result.value["placeholder1"],
                placeholder2=result.value["placeholder2"],
            )
        else:
            return None

    ###########################
    #### Global Parameters ####
    ###########################

    @property
    def block(self) -> int:
        r"""Returns current chain block.
        Returns:
            block (int):
                Current chain block.
        """
        return self.get_current_block()

    def total_issuance(self, block: Optional[int] = None) -> "Balance":
        """
        Retrieves the total issuance of the nimble network's native token (Nim) as of a specific
        blockchain block. This represents the total amount of currency that has been issued or mined on the network.

        Args:
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            Balance: The total issuance of Nim, represented as a Balance object.

        The total issuance is a key economic indicator in the nimble network, reflecting the overall supply
        of the currency and providing insights into the network's economic health and inflationary trends.
        """
        return Balance.from_vim(
            self.query_nbnetwork("TotalIssuance", block).value
        )

    def total_stake(self, block: Optional[int] = None) -> "Balance":
        """
        Retrieves the total amount of Nim staked on the nimble network as of a specific blockchain block.
        This represents the cumulative stake across all particles in the network, indicating the overall level
        of participation and investment by the network's participants.

        Args:
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            Balance: The total amount of Nim staked on the network, represented as a Balance object.

        The total stake is an important metric for understanding the network's security, governance dynamics,
        and the level of commitment by its participants. It is also a critical factor in the network's
        consensus and incentive mechanisms.
        """
        return Balance.from_vim(self.query_nbnetwork("TotalStake", block).value)

    def serving_rate_limit(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[int]:
        """
        Retrieves the serving rate limit for a specific cosmos within the nimble network.
        This rate limit determines the maximum number of requests a particle can serve within a given time frame.

        Args:
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            Optional[int]: The serving rate limit of the cosmos if it exists, None otherwise.

        The serving rate limit is a crucial parameter for maintaining network efficiency and preventing
        overuse of resources by individual particles. It helps ensure a balanced distribution of service
        requests across the network.
        """
        if not self.cosmos_exists(netuid, block):
            return None
        return self.query_nbnetwork(
            "ServingRateLimit", block=block, params=[netuid]
        ).value

    def tx_rate_limit(self, block: Optional[int] = None) -> Optional[int]:
        """
        Retrieves the transaction rate limit for the nimble network as of a specific blockchain block.
        This rate limit sets the maximum number of transactions that can be processed within a given time frame.

        Args:
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            Optional[int]: The transaction rate limit of the network, None if not available.

        The transaction rate limit is an essential parameter for ensuring the stability and scalability
        of the nimble network. It helps in managing network load and preventing congestion, thereby
        maintaining efficient and timely transaction processing.
        """
        return self.query_nbnetwork("TxRateLimit", block).value

    #####################################
    #### Network Parameters ####
    #####################################

    def cosmos_exists(self, netuid: int, block: Optional[int] = None) -> bool:
        """
        Checks if a cosmos with the specified unique identifier (netuid) exists within the nimble network.

        Args:
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number at which to check the cosmos's existence.

        Returns:
            bool: True if the cosmos exists, False otherwise.

        This function is critical for verifying the presence of specific cosmos in the network,
        enabling a deeper understanding of the network's structure and composition.
        """
        return self.query_nbnetwork("NetworksAdded", block, [netuid]).value

    def get_all_cosmos_netuids(self, block: Optional[int] = None) -> List[int]:
        """
        Retrieves the list of all cosmos unique identifiers (netuids) currently present in the nimble network.

        Args:
            block (Optional[int], optional): The blockchain block number at which to retrieve the cosmos netuids.

        Returns:
            List[int]: A list of cosmos netuids.

        This function provides a comprehensive view of the cosmos within the nimble network,
        offering insights into its diversity and scale.
        """
        cosmos_netuids = []
        result = self.query_map_nbnetwork("NetworksAdded", block)
        if result.records:
            for netuid, exists in result:
                if exists:
                    cosmos_netuids.append(netuid.value)

        return cosmos_netuids

    def get_total_cosmos(self, block: Optional[int] = None) -> int:
        """
        Retrieves the total number of cosmos within the nimble network as of a specific blockchain block.

        Args:
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            int: The total number of cosmos in the network.

        Understanding the total number of cosmos is essential for assessing the network's growth and
        the extent of its decentralized infrastructure.
        """
        return self.query_nbnetwork("TotalNetworks", block).value

    def get_cosmos_modality(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[int]:
        return self.query_nbnetwork("NetworkModality", block, [netuid]).value

    def get_cosmos_connection_requirement(
        self, netuid_0: int, netuid_1: int, block: Optional[int] = None
    ) -> Optional[int]:
        return self.query_nbnetwork(
            "NetworkConnect", block, [netuid_0, netuid_1]
        ).value

    def get_emission_value_by_cosmos(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[float]:
        """
        Retrieves the emission value of a specific cosmos within the nimble network. The emission value
        represents the rate at which the cosmos emits or distributes the network's native token (Nim).

        Args:
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[float]: The emission value of the cosmos, None if not available.

        The emission value is a critical economic parameter, influencing the incentive distribution and
        reward mechanisms within the cosmos.
        """
        return Balance.from_vim(
            self.query_nbnetwork("EmissionValues", block, [netuid]).value
        )

    def get_cosmos_connection_requirements(
        self, netuid: int, block: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Retrieves the connection requirements for a specific cosmos within the nimble network. This
        function provides details on the criteria that must be met for particles to connect to the cosmos.

        Args:
            netuid (int): The network UID of the cosmos to query.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Dict[str, int]: A dictionary detailing the connection requirements for the cosmos.

        Understanding these requirements is crucial for particles looking to participate in or interact
        with specific cosmos, ensuring compliance with their connection standards.
        """
        result = self.query_map_nbnetwork("NetworkConnect", block, [netuid])
        if result.records:
            requirements = {}
            for tuple in result.records:
                requirements[str(tuple[0].value)] = tuple[1].value
        else:
            return {}

    def get_cosmos(self, block: Optional[int] = None) -> List[int]:
        """
        Retrieves a list of all cosmos currently active within the nimble network. This function
        provides an overview of the various cosmos and their identifiers.

        Args:
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            List[int]: A list of network UIDs representing each active cosmos.

        This function is valuable for understanding the network's structure and the diversity of cosmos
        available for particle participation and collaboration.
        """
        cosmos = []
        result = self.query_map_nbnetwork("NetworksAdded", block)
        if result.records:
            for network in result.records:
                cosmos.append(network[0].value)
            return cosmos
        else:
            return []

    def get_all_cosmos_info(
        self, block: Optional[int] = None
    ) -> List[CosmosInfo]:
        """
        Retrieves detailed information about all cosmos within the nimble network. This function
        provides comprehensive data on each cosmos, including its characteristics and operational parameters.

        Args:
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            List[CosmosInfo]: A list of CosmosInfo objects, each containing detailed information about a cosmos.

        Gaining insights into the cosmos' details assists in understanding the network's composition,
        the roles of different cosmos, and their unique features.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                block_hash = (
                    None if block == None else substrate.get_block_hash(block)
                )
                params = []
                if block_hash:
                    params = params + [block_hash]
                return substrate.rpc_request(
                    method="cosmosInfo_getCosmossInfo",  # custom rpc method
                    params=params,
                )

        json_body = make_substrate_call_with_retry()
        result = json_body["result"]

        if result in (None, []):
            return []

        return CosmosInfo.list_from_vec_u8(result)

    def get_cosmos_info(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[CosmosInfo]:
        """
        Retrieves detailed information about a specific cosmos within the nimble network. This function
        provides key data on the cosmos, including its operational parameters and network status.

        Args:
            netuid (int): The network UID of the cosmos to query.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[CosmosInfo]: Detailed information about the cosmos, or None if not found.

        This function is essential for particles and stakeholders interested in the specifics of a particular
        cosmos, including its governance, performance, and role within the broader network.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                block_hash = (
                    None if block == None else substrate.get_block_hash(block)
                )
                params = [netuid]
                if block_hash:
                    params = params + [block_hash]
                return substrate.rpc_request(
                    method="cosmosInfo_getCosmosInfo",  # custom rpc method
                    params=params,
                )

        json_body = make_substrate_call_with_retry()
        result = json_body["result"]

        if result in (None, []):
            return None

        return CosmosInfo.from_vec_u8(result)

    def get_cosmos_hyperparameters(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[CosmosHyperparameters]:
        """
        Retrieves the hyperparameters for a specific cosmos within the nimble network. These hyperparameters
        define the operational settings and rules governing the cosmos's behavior.

        Args:
            netuid (int): The network UID of the cosmos to query.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[CosmosHyperparameters]: The cosmos's hyperparameters, or None if not available.

        Understanding the hyperparameters is crucial for comprehending how cosmos are configured and
        managed, and how they interact with the network's consensus and incentive mechanisms.
        """
        hex_bytes_result = self.query_runtime_api(
            runtime_api="CosmosInfoRuntimeApi",
            method="get_cosmos_hyperparams",
            params=[netuid],
            block=block,
        )

        if hex_bytes_result == None:
            return []

        if hex_bytes_result.startswith("0x"):
            bytes_result = bytes.fromhex(hex_bytes_result[2:])
        else:
            bytes_result = bytes.fromhex(hex_bytes_result)

        return CosmosHyperparameters.from_vec_u8(bytes_result)

    def get_cosmos_owner(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[str]:
        """
        Retrieves the owner's address of a specific cosmos within the nimble network. The owner is
        typically the entity responsible for the creation and maintenance of the cosmos.

        Args:
            netuid (int): The network UID of the cosmos to query.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[str]: The SS58 address of the cosmos's owner, or None if not available.

        Knowing the cosmos owner provides insights into the governance and operational control of the cosmos,
        which can be important for decision-making and collaboration within the network.
        """
        return self.query_nbnetwork("CosmosOwner", block, [netuid]).value

    ###########################
    #### Stake Information ####
    ###########################

    def get_stake_info_for_coldkey(
        self, coldkey_ss58: str, block: Optional[int] = None
    ) -> List[StakeInfo]:
        """
        Retrieves stake information associated with a specific coldkey. This function provides details
        about the stakes held by an account, including the staked amounts and associated delegates.

        Args:
            coldkey_ss58 (str): The SS58 address of the account's coldkey.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            List[StakeInfo]: A list of StakeInfo objects detailing the stake allocations for the account.

        Stake information is vital for account holders to assess their investment and participation
        in the network's delegation and consensus processes.
        """
        encoded_coldkey = ss58_to_vec_u8(coldkey_ss58)

        hex_bytes_result = self.query_runtime_api(
            runtime_api="StakeInfoRuntimeApi",
            method="get_stake_info_for_coldkey",
            params=[encoded_coldkey],
            block=block,
        )

        if hex_bytes_result == None:
            return None

        if hex_bytes_result.startswith("0x"):
            bytes_result = bytes.fromhex(hex_bytes_result[2:])
        else:
            bytes_result = bytes.fromhex(hex_bytes_result)

        return StakeInfo.list_from_vec_u8(bytes_result)

    def get_stake_info_for_coldkeys(
        self, coldkey_ss58_list: List[str], block: Optional[int] = None
    ) -> Dict[str, List[StakeInfo]]:
        """
        Retrieves stake information for a list of coldkeys. This function aggregates stake data for multiple
        accounts, providing a collective view of their stakes and delegations.

        Args:
            coldkey_ss58_list (List[str]): A list of SS58 addresses of the accounts' coldkeys.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Dict[str, List[StakeInfo]]: A dictionary mapping each coldkey to a list of its StakeInfo objects.

        This function is useful for analyzing the stake distribution and delegation patterns of multiple
        accounts simultaneously, offering a broader perspective on network participation and investment strategies.
        """
        encoded_coldkeys = [
            ss58_to_vec_u8(coldkey_ss58) for coldkey_ss58 in coldkey_ss58_list
        ]

        hex_bytes_result = self.query_runtime_api(
            runtime_api="StakeInfoRuntimeApi",
            method="get_stake_info_for_coldkeys",
            params=[encoded_coldkeys],
            block=block,
        )

        if hex_bytes_result == None:
            return None

        if hex_bytes_result.startswith("0x"):
            bytes_result = bytes.fromhex(hex_bytes_result[2:])
        else:
            bytes_result = bytes.fromhex(hex_bytes_result)

        return StakeInfo.list_of_tuple_from_vec_u8(bytes_result)

    ########################################
    #### Particle information per cosmos ####
    ########################################

    def is_hotkey_registered_any(
        self, hotkey_ss58: str, block: Optional[int] = None
    ) -> bool:
        """
        Checks if a particle's hotkey is registered on any cosmos within the nimble network.

        Args:
            hotkey_ss58 (str): The SS58 address of the particle's hotkey.
            block (Optional[int], optional): The blockchain block number at which to perform the check.

        Returns:
            bool: True if the hotkey is registered on any cosmos, False otherwise.

        This function is essential for determining the network-wide presence and participation of a particle.
        """
        return len(self.get_netuids_for_hotkey(hotkey_ss58, block)) > 0

    def is_hotkey_registered_on_cosmos(
        self, hotkey_ss58: str, netuid: int, block: Optional[int] = None
    ) -> bool:
        """
        Checks if a particle's hotkey is registered on a specific cosmos within the nimble network.

        Args:
            hotkey_ss58 (str): The SS58 address of the particle's hotkey.
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number at which to perform the check.

        Returns:
            bool: True if the hotkey is registered on the specified cosmos, False otherwise.

        This function helps in assessing the participation of a particle in a particular cosmos,
        indicating its specific area of operation or influence within the network.
        """
        return (
            self.get_uid_for_hotkey_on_cosmos(hotkey_ss58, netuid, block)
            != None
        )

    def is_hotkey_registered(
        self,
        hotkey_ss58: str,
        netuid: Optional[int] = None,
        block: Optional[int] = None,
    ) -> bool:
        """
        Determines whether a given hotkey (public key) is registered in the nimble network, either
        globally across any cosmos or specifically on a specified cosmos. This function checks the registration
        status of a particle identified by its hotkey, which is crucial for validating its participation and
        activities within the network.

        Args:
            hotkey_ss58 (str): The SS58 address of the particle's hotkey.
            netuid (Optional[int], optional): The unique identifier of the cosmos to check the registration.
                                            If None, the registration is checked across all cosmos.
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            bool: True if the hotkey is registered in the specified context (either any cosmos or a specific cosmos),
                False otherwise.

        This function is important for verifying the active status of particles in the nimble network. It aids
        in understanding whether a particle is eligible to participate in network processes such as consensus,
        validation, and incentive distribution based on its registration status.
        """
        if netuid == None:
            return self.is_hotkey_registered_any(hotkey_ss58, block)
        else:
            return self.is_hotkey_registered_on_cosmos(
                hotkey_ss58, netuid, block
            )

    def get_uid_for_hotkey_on_cosmos(
        self, hotkey_ss58: str, netuid: int, block: Optional[int] = None
    ) -> Optional[int]:
        """
        Retrieves the unique identifier (UID) for a particle's hotkey on a specific cosmos.

        Args:
            hotkey_ss58 (str): The SS58 address of the particle's hotkey.
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[int]: The UID of the particle if it is registered on the cosmos, None otherwise.

        The UID is a critical identifier within the network, linking the particle's hotkey to its
        operational and governance activities on a particular cosmos.
        """
        return self.query_nbnetwork("Uids", block, [netuid, hotkey_ss58]).value

    def get_all_uids_for_hotkey(
        self, hotkey_ss58: str, block: Optional[int] = None
    ) -> List[int]:
        """
        Retrieves all unique identifiers (UIDs) associated with a given hotkey across different cosmos
        within the nimble network. This function helps in identifying all the particle instances that are
        linked to a specific hotkey.

        Args:
            hotkey_ss58 (str): The SS58 address of the particle's hotkey.
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            List[int]: A list of UIDs associated with the given hotkey across various cosmos.

        This function is important for tracking a particle's presence and activities across different
        cosmos within the nimble ecosystem.
        """
        return [
            self.get_uid_for_hotkey_on_cosmos(hotkey_ss58, netuid, block)
            for netuid in self.get_netuids_for_hotkey(hotkey_ss58, block)
        ]

    def get_netuids_for_hotkey(
        self, hotkey_ss58: str, block: Optional[int] = None
    ) -> List[int]:
        """
        Retrieves a list of cosmos UIDs (netuids) for which a given hotkey is a member. This function
        identifies the specific cosmos within the nimble network where the particle associated with
        the hotkey is active.

        Args:
            hotkey_ss58 (str): The SS58 address of the particle's hotkey.
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            List[int]: A list of netuids where the particle is a member.

        This function provides insights into a particle's involvement and distribution across different
        cosmos, illustrating its role and contributions within the network.
        """
        result = self.query_map_nbnetwork(
            "IsNetworkMember", block, [hotkey_ss58]
        )
        netuids = []
        for netuid, is_member in result.records:
            if is_member:
                netuids.append(netuid.value)
        return netuids

    def get_particle_for_pubkey_and_cosmos(
        self, hotkey_ss58: str, netuid: int, block: Optional[int] = None
    ) -> Optional[ParticleInfo]:
        """
        Retrieves information about a particle based on its public key (hotkey SS58 address) and the specific
        cosmos UID (netuid). This function provides detailed particle information for a particular cosmos within
        the nimble network.

        Args:
            hotkey_ss58 (str): The SS58 address of the particle's hotkey.
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            Optional[ParticleInfo]: Detailed information about the particle if found, None otherwise.

        This function is crucial for accessing specific particle data and understanding its status, stake,
        and other attributes within a particular cosmos of the nimble ecosystem.
        """
        return self.particle_for_uid(
            self.get_uid_for_hotkey_on_cosmos(hotkey_ss58, netuid, block=block),
            netuid,
            block=block,
        )

    def get_all_particles_for_pubkey(
        self, hotkey_ss58: str, block: Optional[int] = None
    ) -> List[ParticleInfo]:
        """
        Retrieves information about all particle instances associated with a given public key (hotkey SS58
        address) across different cosmos of the nimble network. This function aggregates particle data
        from various cosmos to provide a comprehensive view of a particle's presence and status within the network.

        Args:
            hotkey_ss58 (str): The SS58 address of the particle's hotkey.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            List[ParticleInfo]: A list of ParticleInfo objects detailing the particle's presence across various cosmos.

        This function is valuable for analyzing a particle's overall participation, influence, and
        contributions across the nimble network.
        """
        netuids = self.get_netuids_for_hotkey(hotkey_ss58, block)
        uids = [
            self.get_uid_for_hotkey_on_cosmos(hotkey_ss58, net)
            for net in netuids
        ]
        return [
            self.particle_for_uid(uid, net)
            for uid, net in list(zip(uids, netuids))
        ]

    def particle_has_validator_permit(
        self, uid: int, netuid: int, block: Optional[int] = None
    ) -> Optional[bool]:
        """
        Checks if a particle, identified by its unique identifier (UID), has a validator permit on a specific
        cosmos within the nimble network. This function determines whether the particle is authorized to
        participate in validation processes on the cosmos.

        Args:
            uid (int): The unique identifier of the particle.
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[bool]: True if the particle has a validator permit, False otherwise.

        This function is essential for understanding a particle's role and capabilities within a specific
        cosmos, particularly regarding its involvement in network validation and governance.
        """
        return self.query_nbnetwork(
            "ValidatorPermit", block, [netuid, uid]
        ).value

    def particle_for_wallet(
        self, wallet: "nimlib.wallet", netuid: int, block: Optional[int] = None
    ) -> Optional[ParticleInfo]:
        """
        Retrieves information about a particle associated with a given wallet on a specific cosmos.
        This function provides detailed data about the particle's status, stake, and activities based on
        the wallet's hotkey address.

        Args:
            wallet (nimlib.wallet): The wallet associated with the particle.
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number at which to perform the query.

        Returns:
            Optional[ParticleInfo]: Detailed information about the particle if found, None otherwise.

        This function is important for wallet owners to understand and manage their particle's presence
        and activities within a particular cosmos of the nimble network.
        """
        return self.get_particle_for_pubkey_and_cosmos(
            wallet.hotkey.ss58_address, netuid=netuid, block=block
        )

    def particle_for_uid(
        self, uid: int, netuid: int, block: Optional[int] = None
    ) -> Optional[ParticleInfo]:
        """
        Retrieves detailed information about a specific particle identified by its unique identifier (UID)
        within a specified cosmos (netuid) of the nimble network. This function provides a comprehensive
        view of a particle's attributes, including its stake, rank, and operational status.

        Args:
            uid (int): The unique identifier of the particle.
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[ParticleInfo]: Detailed information about the particle if found, None otherwise.

        This function is crucial for analyzing individual particles' contributions and status within a specific
        cosmos, offering insights into their roles in the network's consensus and validation mechanisms.
        """
        if uid == None:
            return ParticleInfo._null_particle()

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                block_hash = (
                    None if block == None else substrate.get_block_hash(block)
                )
                params = [netuid, uid]
                if block_hash:
                    params = params + [block_hash]
                return substrate.rpc_request(
                    method="particleInfo_getParticle",
                    params=params,  # custom rpc method
                )

        json_body = make_substrate_call_with_retry()
        result = json_body["result"]

        if result in (None, []):
            return ParticleInfo._null_particle()

        return ParticleInfo.from_vec_u8(result)

    def particles(
        self, netuid: int, block: Optional[int] = None
    ) -> List[ParticleInfo]:
        """
        Retrieves a list of all particles within a specified cosmos of the nimble network. This function
        provides a snapshot of the cosmos's particle population, including each particle's attributes and network
        interactions.

        Args:
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            List[ParticleInfo]: A list of ParticleInfo objects detailing each particle's characteristics in the cosmos.

        Understanding the distribution and status of particles within a cosmos is key to comprehending the
        network's decentralized structure and the dynamics of its consensus and governance processes.
        """
        particles_lite = self.particles_lite(netuid=netuid, block=block)
        weights = self.weights(block=block, netuid=netuid)
        bonds = self.bonds(block=block, netuid=netuid)

        weights_as_dict = {uid: w for uid, w in weights}
        bonds_as_dict = {uid: b for uid, b in bonds}

        particles = [
            ParticleInfo.from_weights_bonds_and_particle_lite(
                particle_lite, weights_as_dict, bonds_as_dict
            )
            for particle_lite in particles_lite
        ]

        return particles

    def particle_for_uid_lite(
        self, uid: int, netuid: int, block: Optional[int] = None
    ) -> Optional[ParticleInfoLite]:
        """
        Retrieves a lightweight version of information about a particle in a specific cosmos, identified by
        its UID. The 'lite' version focuses on essential attributes such as stake and network activity.

        Args:
            uid (int): The unique identifier of the particle.
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[ParticleInfoLite]: A simplified version of particle information if found, None otherwise.

        This function is useful for quick and efficient analyses of particle status and activities within a
        cosmos without the need for comprehensive data retrieval.
        """
        if uid == None:
            return ParticleInfoLite._null_particle()

        hex_bytes_result = self.query_runtime_api(
            runtime_api="ParticleInfoRuntimeApi",
            method="get_particle_lite",
            params={
                "netuid": netuid,
                "uid": uid,
            },
            block=block,
        )

        if hex_bytes_result == None:
            return ParticleInfoLite._null_particle()

        if hex_bytes_result.startswith("0x"):
            bytes_result = bytes.fromhex(hex_bytes_result[2:])
        else:
            bytes_result = bytes.fromhex(hex_bytes_result)

        return ParticleInfoLite.from_vec_u8(bytes_result)

    def particles_lite(
        self, netuid: int, block: Optional[int] = None
    ) -> List[ParticleInfoLite]:
        """
        Retrieves a list of particles in a 'lite' format from a specific cosmos of the nimble network.
        This function provides a streamlined view of the particles, focusing on key attributes such as stake
        and network participation.

        Args:
            netuid (int): The unique identifier of the cosmos.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            List[ParticleInfoLite]: A list of simplified particle information for the cosmos.

        This function offers a quick overview of the particle population within a cosmos, facilitating
        efficient analysis of the network's decentralized structure and particle dynamics.
        """
        hex_bytes_result = self.query_runtime_api(
            runtime_api="ParticleInfoRuntimeApi",
            method="get_particles_lite",
            params=[netuid],
            block=block,
        )

        if hex_bytes_result == None:
            return []

        if hex_bytes_result.startswith("0x"):
            bytes_result = bytes.fromhex(hex_bytes_result[2:])
        else:
            bytes_result = bytes.fromhex(hex_bytes_result)

        return ParticleInfoLite.list_from_vec_u8(bytes_result)

    def megastring(
        self,
        netuid: int,
        lite: bool = True,
        block: Optional[int] = None,
    ) -> "nimlib.Megastring":
        """
        Returns a synced megastring for a specified cosmos within the nimble network. The megastring
        represents the network's structure, including particle connections and interactions.

        Args:
            netuid (int): The network UID of the cosmos to query.
            lite (bool, default=True): If true, returns a megastring using a lightweight sync (no weights, no bonds).
            block (Optional[int]): Block number for synchronization, or None for the latest block.

        Returns:
            nimlib.Megastring: The megastring representing the cosmos's structure and particle relationships.

        The megastring is an essential tool for understanding the topology and dynamics of the nimble
        network's decentralized architecture, particularly in relation to particle interconnectivity and consensus processes.
        """
        megastring_ = nimlib.megastring(
            network=self.network, netuid=netuid, lite=lite, sync=False
        )
        megastring_.sync(block=block, lite=lite, nbnetwork=self)

        return megastring_

    def incentive(self, netuid: int, block: Optional[int] = None) -> List[int]:
        """
        Retrieves the list of incentives for particles within a specific cosmos of the nimble network.
        This function provides insights into the reward distribution mechanisms and the incentives allocated
        to each particle based on their contributions and activities.

        Args:
            netuid (int): The network UID of the cosmos to query.
            block (Optional[int]): The blockchain block number for the query.

        Returns:
            List[int]: The list of incentives for particles within the cosmos, indexed by UID.

        Understanding the incentive structure is crucial for analyzing the network's economic model and
        the motivational drivers for particle participation and collaboration.
        """
        i_map = []
        i_map_encoded = self.query_map_nbnetwork(name="Incentive", block=block)
        if i_map_encoded.records:
            for netuid_, incentives_map in i_map_encoded:
                if netuid_ == netuid:
                    i_map = incentives_map.serialize()
                    break

        return i_map

    def weights(
        self, netuid: int, block: Optional[int] = None
    ) -> List[Tuple[int, List[Tuple[int, int]]]]:
        """
        Retrieves the weight distribution set by particles within a specific cosmos of the nimble network.
        This function maps each particle's UID to the weights it assigns to other particles, reflecting the
        network's trust and value assignment mechanisms.

        Args:
            netuid (int): The network UID of the cosmos to query.
            block (Optional[int]): The blockchain block number for the query.

        Returns:
            List[Tuple[int, List[Tuple[int, int]]]]: A list of tuples mapping each particle's UID to its assigned weights.

        The weight distribution is a key factor in the network's consensus algorithm and the ranking of particles,
        influencing their influence and reward allocation within the cosmos.
        """
        w_map = []
        w_map_encoded = self.query_map_nbnetwork(
            name="Weights", block=block, params=[netuid]
        )
        if w_map_encoded.records:
            for uid, w in w_map_encoded:
                w_map.append((uid.serialize(), w.serialize()))

        return w_map

    def bonds(
        self, netuid: int, block: Optional[int] = None
    ) -> List[Tuple[int, List[Tuple[int, int]]]]:
        """
        Retrieves the bond distribution set by particles within a specific cosmos of the nimble network.
        Bonds represent the investments or commitments made by particles in one another, indicating a level
        of trust and perceived value. This bonding mechanism is integral to the network's market-based approach
        to measuring and rewarding machine intelligence.

        Args:
            netuid (int): The network UID of the cosmos to query.
            block (Optional[int]): The blockchain block number for the query.

        Returns:
            List[Tuple[int, List[Tuple[int, int]]]]: A list of tuples mapping each particle's UID to its bonds with other particles.

        Understanding bond distributions is crucial for analyzing the trust dynamics and market behavior
        within the cosmos. It reflects how particles recognize and invest in each other's intelligence and
        contributions, supporting diverse and niche systems within the nimble ecosystem.
        """
        b_map = []
        b_map_encoded = self.query_map_nbnetwork(
            name="Bonds", block=block, params=[netuid]
        )
        if b_map_encoded.records:
            for uid, b in b_map_encoded:
                b_map.append((uid.serialize(), b.serialize()))

        return b_map

    def associated_validator_ip_info(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[List[IPInfo]]:
        """
        Retrieves the list of all validator IP addresses associated with a specific cosmos in the nimble
        network. This information is crucial for network communication and the identification of validator nodes.

        Args:
            netuid (int): The network UID of the cosmos to query.
            block (Optional[int]): The blockchain block number for the query.

        Returns:
            Optional[List[IPInfo]]: A list of IPInfo objects for validator nodes in the cosmos, or None if no validators are associated.

        Validator IP information is key for establishing secure and reliable connections within the network,
        facilitating consensus and validation processes critical for the network's integrity and performance.
        """
        hex_bytes_result = self.query_runtime_api(
            runtime_api="ValidatorIPRuntimeApi",
            method="get_associated_validator_ip_info_for_cosmos",
            params=[netuid],
            block=block,
        )

        if hex_bytes_result == None:
            return None

        if hex_bytes_result.startswith("0x"):
            bytes_result = bytes.fromhex(hex_bytes_result[2:])
        else:
            bytes_result = bytes.fromhex(hex_bytes_result)

        return IPInfo.list_from_vec_u8(bytes_result)

    def get_cosmos_burn_cost(self, block: Optional[int] = None) -> int:
        """
        Retrieves the burn cost for registering a new cosmos within the nimble network. This cost
        represents the amount of Nim that needs to be locked or burned to establish a new cosmos.

        Args:
            block (Optional[int]): The blockchain block number for the query.

        Returns:
            int: The burn cost for cosmos registration.

        The cosmos burn cost is an important economic parameter, reflecting the network's mechanisms for
        controlling the proliferation of cosmos and ensuring their commitment to the network's long-term viability.
        """
        lock_cost = self.query_runtime_api(
            runtime_api="CosmosRegistrationRuntimeApi",
            method="get_network_registration_cost",
            params=[],
            block=block,
        )

        if lock_cost == None:
            return None

        return lock_cost

    ################
    #### Legacy ####
    ################

    def get_balance(self, address: str, block: int = None) -> Balance:
        """
        Retrieves the token balance of a specific address within the nimble network. This function queries
        the blockchain to determine the amount of Nim held by a given account.

        Args:
            address (str): The Substrate address in ss58 format.
            block (int, optional): The blockchain block number at which to perform the query.

        Returns:
            Balance: The account balance at the specified block, represented as a Balance object.

        This function is important for monitoring account holdings and managing financial transactions
        within the nimble ecosystem. It helps in assessing the economic status and capacity of network participants.
        """
        try:

            @retry(delay=2, tries=3, backoff=2, max_delay=4)
            def make_substrate_call_with_retry():
                with self.substrate as substrate:
                    return substrate.query(
                        module="System",
                        storage_function="Account",
                        params=[address],
                        block_hash=None
                        if block == None
                        else substrate.get_block_hash(block),
                    )

            result = make_substrate_call_with_retry()
        except scalecodec.exceptions.RemainingScaleBytesNotEmptyException:
            nimlib.logging.error(
                "Your wallet it legacy formatted, you need to run nbcli stake --ammount 0 to reformat it."
            )
            return Balance(1000)
        return Balance(result.value["data"]["free"])

    def get_current_block(self) -> int:
        """
        Returns the current block number on the nimble blockchain. This function provides the latest block
        number, indicating the most recent state of the blockchain.

        Returns:
            int: The current chain block number.

        Knowing the current block number is essential for querying real-time data and performing time-sensitive
        operations on the blockchain. It serves as a reference point for network activities and data synchronization.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                return substrate.get_block_number(None)

        return make_substrate_call_with_retry()

    def get_balances(self, block: int = None) -> Dict[str, Balance]:
        """
        Retrieves the token balances of all accounts within the nimble network as of a specific blockchain block.
        This function provides a comprehensive view of the token distribution among different accounts.

        Args:
            block (int, optional): The blockchain block number at which to perform the query.

        Returns:
            Dict[str, Balance]: A dictionary mapping each account's ss58 address to its balance.

        This function is valuable for analyzing the overall economic landscape of the nimble network,
        including the distribution of financial resources and the financial status of network participants.
        """

        @retry(delay=2, tries=3, backoff=2, max_delay=4)
        def make_substrate_call_with_retry():
            with self.substrate as substrate:
                return substrate.query_map(
                    module="System",
                    storage_function="Account",
                    block_hash=None
                    if block == None
                    else substrate.get_block_hash(block),
                )

        result = make_substrate_call_with_retry()
        return_dict = {}
        for r in result:
            bal = Balance(int(r[1]["data"]["free"].value))
            return_dict[r[0].value] = bal
        return return_dict

    ################
    ## Extrinsics ##
    ################
    @staticmethod
    def _null_particle() -> ParticleInfo:
        particle = ParticleInfo(
            uid=0,
            netuid=0,
            active=0,
            stake="0",
            rank=0,
            emission=0,
            incentive=0,
            consensus=0,
            trust=0,
            validator_trust=0,
            dividends=0,
            last_update=0,
            validator_permit=False,
            weights=[],
            bonds=[],
            proton_info=None,
            fermion_info=None,
            is_null=True,
            coldkey="000000000000000000000000000000000000000000000000",
            hotkey="000000000000000000000000000000000000000000000000",
        )
        return particle

    def get_block_hash(self, block_id: int) -> str:
        """
        Retrieves the hash of a specific block on the nimble blockchain. The block hash is a unique
        identifier representing the cryptographic hash of the block's content, ensuring its integrity and
        immutability.

        Args:
            block_id (int): The block number for which the hash is to be retrieved.

        Returns:
            str: The cryptographic hash of the specified block.

        The block hash is a fundamental aspect of blockchain technology, providing a secure reference to
        each block's data. It is crucial for verifying transactions, ensuring data consistency, and
        maintaining the trustworthiness of the blockchain.
        """
        return self.substrate.get_block_hash(block_id=block_id)

    def burn(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[Balance]:
        """
        Retrieves the 'Burn' hyperparameter for a specified subnet. The 'Burn' parameter represents the
        amount of Nim that is effectively removed from circulation within the nimble network.

        Args:
            netuid (int): The unique identifier of the subnet.
            block (Optional[int], optional): The blockchain block number for the query.

        Returns:
            Optional[Balance]: The value of the 'Burn' hyperparameter if the subnet exists, None otherwise.

        Understanding the 'Burn' rate is essential for analyzing the network's economic model, particularly
        how it manages inflation and the overall supply of its native token Nim.
        """
        if not self.cosmos_exists(netuid, block):
            return None
        return Balance.from_vim(
            self.query_nbnetwork("Burn", block, [netuid]).value
        )
