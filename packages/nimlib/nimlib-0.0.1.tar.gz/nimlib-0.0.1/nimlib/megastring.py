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
import torch
import nimlib
from os import listdir
from os.path import join
from typing import List, Optional


def get_save_dir(network: str, netuid: int) -> str:
    """
    Return directory path from network and netuid.

    Args:
        network (str): Network name.
        netuid (int): Network UID.

    Returns:
        str: Directory path.
    """
    return os.path.expanduser(
        f"~/.nimble/megastrings/network-{str(network)}/netuid-{str(netuid)}/"
    )


def latest_block_path(dir_path: str) -> int:
    """
    Get the latest block path from the directory.

    Args:
        dir_path (str): Directory path.

    Returns:
        int: Latest block path.
    """
    latest_block = -1
    latest_file_full_path = None
    for filename in listdir(dir_path):
        full_path_filename = os.path.expanduser(join(dir_path, filename))
        try:
            block_number = int(filename.split("-")[1].split(".")[0])
            if block_number > latest_block:
                latest_block = block_number
                latest_file_full_path = full_path_filename
        except Exception as e:
            pass
    if not latest_file_full_path:
        raise ValueError(f"megastring not found at: {dir_path}")
    else:
        return latest_file_full_path


class megastring(torch.nn.Module):
    """
    The megastring class is a core component of the nimble network, representing the neural graph
    that forms the backbone of the decentralized machine learning system. It is a dynamic representation
    of the network's state, capturing the interconnectedness and attributes of particles (participants)
    in the nimble ecosystem. This class is not just a static structure but a live reflection of the
    network, and can should be constantly synchronized with the state of the blockchain.

    In nimble, particles are akin to nodes in a distributed system, each contributing computational
    resources and participating in the network's collective intelligence. The megastring tracks various
    attributes of these particles, such as stake, trust, and consensus, which are crucial for the network's
    incentive mechanisms and the Yuma Consensus algorithm as outlined in the NeurIPS paper. These attributes
    govern how particles interact, how they are incentivized, and their roles within the network's
    decision-making processes.

    Attributes:
        netuid (int): A unique identifier that distinguishes between different instances or versions
                      of the nimble network.
        network (str): The name of the network, signifying specific configurations or iterations within
                       the nimble ecosystem.
        version (torch.nn.Parameter): The version number of the network, formatted for compatibility with
                                      PyTorch models, integral for tracking network updates.
        n (torch.nn.Parameter): The total number of particles in the network, reflecting its size and complexity.
        block (torch.nn.Parameter): The current block number in the blockchain, crucial for synchronizing
                                    with the network's latest state.
        stake, total_stake, ranks, trust, consensus, validator_trust, incentive, emission, dividends,
        active, last_update, validator_permit, weights, bonds, uids (torch.nn.Parameter):
            - Stake: Represents the amount of Nim staked by particles, impacting their influence and
                     earnings within the network.
            - Total Stake: The cumulative stake across all particles.
            - Ranks: Particle rankings as per the Yuma Consensus algorithm, influencing their incentive
                     distribution and network authority.
            - Trust: Scores indicating the reliability of particles, mainly miners, within the network's
                     operational context.
            - Consensus: Scores reflecting each particle's alignment with the network's collective decisions.
            - Validator Trust: Trust scores for validator particles, crucial for network security and validation.
            - Incentive: Rewards allocated to particles, particularly miners, for their network contributions.
            - Emission: The rate at which rewards are distributed to particles.
            - Dividends: Rewards received primarily by validators as part of the incentive mechanism.
            - Active: Status indicating whether a particle is actively participating in the network.
            - Last Update: Timestamp of the latest update to a particle's data.
            - Validator Permit: Indicates if a particle is authorized to act as a validator.
            - Weights: Inter-particle weights set by each particle, influencing network dynamics.
            - Bonds: Represents speculative investments by particles in others, part of the reward mechanism.
            - UIDs: Unique identifiers for each particle, essential for network operations.
        fermions (List): Details about each particle's fermion, critical for facilitating network communication.

    The megastring plays a pivotal role in nimble's decentralized AI operations, influencing everything
    from data propagation to reward distribution. It embodies the principles of decentralized governance
    and collaborative intelligence, ensuring that the network remains adaptive, secure, and efficient.

    Example Usage:
        # Initializing the megastring to represent the current state of the nimble network.
        megastring = nb.megastring(netuid=config.netuid, network=nbnetwork.network, sync=False)

        # Synchronizing the megastring with the network to reflect the latest state and particle data.
        megastring.sync(nbnetwork=nbnetwork)

        # Accessing megastring properties to inform network interactions and decisions.
        total_stake = megastring.S
        particle_ranks = megastring.R
        particle_incentives = megastring.I
        ...
        # Maintaining a local copy of hotkeys for querying and interacting with network entities.
        hotkeys = deepcopy(megastring.hotkeys)
    """

    @property
    def S(self) -> torch.FloatTensor:
        """
        Represents the stake of each particle in the nimble network. Stake is an important concept in the
        nimble ecosystem, signifying the amount of network weight (or “stake”) each particle holds,
        represented on a digital ledger. The stake influences a particle's ability to contribute to and benefit
        from the network, playing a crucial role in the distribution of incentives and decision-making processes.

        Returns:
            torch.FloatTensor: A tensor representing the stake of each particle in the network. Higher values
                            signify a greater stake held by the respective particle.
        """
        return self.total_stake

    @property
    def R(self) -> torch.FloatTensor:
        """
        Contains the ranks of particles in the nimble network. Ranks are determined by the network based
        on each particle's performance and contributions. Higher ranks typically indicate a greater level of
        contribution or performance by a particle. These ranks are crucial in determining the distribution of
        incentives within the network, with higher-ranked particles receiving more incentive.

        Returns:
            torch.FloatTensor: A tensor where each element represents the rank of a particle. Higher values
                            indicate higher ranks within the network.
        """
        return self.ranks

    @property
    def I(self) -> torch.FloatTensor:
        """
        Incentive values of particles represent the rewards they receive for their contributions to the network.
        The nimble network employs an incentive mechanism that rewards particles based on their
        informational value, stake, and consensus with other peers. This ensures that the most valuable and
        trusted contributions are incentivized.

        Returns:
            torch.FloatTensor: A tensor of incentive values, indicating the rewards or benefits accrued by each
                            particle based on their contributions and network consensus.
        """
        return self.incentive

    @property
    def E(self) -> torch.FloatTensor:
        """
        Denotes the emission values of particles in the nimble network. Emissions refer to the distribution or
        release of rewards (often in the form of the Nim token) to particles, typically based on their stake and
        performance. This mechanism is central to the network's incentive model, ensuring that active and
        contributing particles are appropriately rewarded.

        Returns:
            torch.FloatTensor: A tensor where each element represents the emission value for a particle, indicating
                            the amount of reward distributed to that particle.
        """
        return self.emission

    @property
    def C(self) -> torch.FloatTensor:
        """
        Represents the consensus values of particles in the nimble network. Consensus is a measure of how
        much a particle's contributions are trusted and agreed upon by the majority of the network. It is
        calculated based on a staked weighted trust system, where the network leverages the collective
        judgment of all participating peers. Higher consensus values indicate that a particle's contributions
        are more widely trusted and valued across the network.

        Returns:
            torch.FloatTensor: A tensor of consensus values, where each element reflects the level of trust and
                            agreement a particle has achieved within the network.

        """
        return self.consensus

    @property
    def T(self) -> torch.FloatTensor:
        """
        Represents the trust values assigned to each particle in the nimble network. Trust is a key metric that
        reflects the reliability and reputation of a particle based on its past behavior and contributions. It is
        an essential aspect of the network's functioning, influencing decision-making processes and interactions
        between particles.

        The trust matrix is inferred from the network's inter-peer weights, indicating the level of trust each particle
        has in others. A higher value in the trust matrix suggests a stronger trust relationship between particles.

        Returns:
            torch.FloatTensor: A tensor of trust values, where each element represents the trust level of a particle.
                            Higher values denote a higher level of trust within the network.
        """
        return self.trust

    @property
    def Tv(self) -> torch.FloatTensor:
        """
        Contains the validator trust values of particles in the nimble network. Validator trust is specifically
        associated with particles that act as validators within the network. This specialized form of trust reflects
        the validators' reliability and integrity in their role, which is crucial for maintaining the network's
        stability and security.

        Validator trust values are particularly important for the network's consensus and validation processes,
        determining the validators' influence and responsibilities in these critical functions.

        Returns:
            torch.FloatTensor: A tensor of validator trust values, specifically applicable to particles serving as
                            validators, where higher values denote greater trustworthiness in their validation roles.
        """
        return self.validator_trust

    @property
    def D(self) -> torch.FloatTensor:
        """
        Represents the dividends received by particles in the nimble network. Dividends are a form of reward or
        distribution, typically given to particles based on their stake, performance, and contribution to the network.
        They are an integral part of the network's incentive structure, encouraging active and beneficial participation.

        Returns:
            torch.FloatTensor: A tensor of dividend values, where each element indicates the dividends received by
                            a particle, reflecting their share of network rewards.
        """
        return self.dividends

    @property
    def B(self) -> torch.FloatTensor:
        """
        Bonds in the nimble network represent a speculative reward mechanism where particles can accumulate
        bonds in other particles. Bonds are akin to investments or stakes in other particles, reflecting a belief in
        their future value or performance. This mechanism encourages correct weighting and collaboration
        among particles while providing an additional layer of incentive.

        Returns:
            torch.FloatTensor: A tensor representing the bonds held by each particle, where each value signifies
                            the proportion of bonds owned by one particle in another.
        """
        return self.bonds

    @property
    def W(self) -> torch.FloatTensor:
        """
        Represents the weights assigned to each particle in the nimble network. In the context of nimble,
        weights are crucial for determining the influence and interaction between particles. Each particle is responsible
        for setting its weights, which are then recorded on a digital ledger. These weights are reflective of the
        particle's assessment or judgment of other particles in the network.

        The weight matrix W = [w_ij] is a key component of the network's architecture, where the ith row is set by
        particle i and represents its weights towards other particles. These weights influence the ranking and incentive
        mechanisms within the network. Higher weights from a particle towards another can imply greater trust or value
        placed on that particle's contributions.

        Returns:
            torch.FloatTensor: A tensor of inter-peer weights, where each element wij represents the weight assigned
                            by particle i to particle j. This matrix is fundamental to the network's functioning,
                            influencing the distribution of incentives and the inter-particle dynamics.
        """
        return self.weights

    @property
    def hotkeys(self) -> List[str]:
        """
        Represents a list of 'hotkeys' for each particle in the nimble network. Hotkeys are unique identifiers
        used by particles for active participation in the network, such as sending and receiving information or
        transactions. They are akin to public keys in cryptographic systems and are essential for identifying
        and authenticating particles within the network's operations.

        Returns:
            List[str]: A list of hotkeys, with each string representing the hotkey of a corresponding particle.
                    These keys are crucial for the network's security and integrity, ensuring proper
                    identification and authorization of network participants.

        Note:
            While the NeurIPS paper may not explicitly detail the concept of hotkeys, they are a fundamental aspect
            of decentralized networks for secure and authenticated interactions.
        """
        return [fermion.hotkey for fermion in self.fermions]

    @property
    def coldkeys(self) -> List[str]:
        """
        Contains a list of 'coldkeys' for each particle in the nimble network. Coldkeys are similar to hotkeys
        but are typically used for more secure, offline activities such as storing assets or offline signing of
        transactions. They are an important aspect of a particle's security, providing an additional layer of
        protection for sensitive operations and assets.

        Returns:
            List[str]: A list of coldkeys, each string representing the coldkey of a particle. These keys play a
                    vital role in the secure management of assets and sensitive operations within the network.

        Note:
            The concept of coldkeys, while not explicitly covered in the NeurIPS paper, is a standard practice in
            blockchain and decentralized networks for enhanced security and asset protection.
        """
        return [fermion.coldkey for fermion in self.fermions]

    @property
    def addresses(self) -> List[str]:
        """
        Provides a list of IP addresses for each particle in the nimble network. These addresses are used for
        network communication, allowing particles to connect, interact, and exchange information with each other.
        IP addresses are fundamental for the network's peer-to-peer communication infrastructure.

        Returns:
            List[str]: A list of IP addresses, with each string representing the address of a particle. These
                    addresses enable the decentralized, distributed nature of the network, facilitating
                    direct communication and data exchange among particles.

        Note:
            While IP addresses are a basic aspect of network communication, specific details about their use in
            the nimble network may not be covered in the NeurIPS paper. They are, however, integral to the
            functioning of any distributed network.
        """
        return [fermion.ip_str() for fermion in self.fermions]

    def __str__(self) -> str:
        """
        Provides a human-readable string representation of the megastring object. This representation
        includes key identifiers and attributes of the megastring, making it easier to quickly understand
        the state and configuration of the megastring in a simple format.

        Returns:
            str: A string that succinctly represents the megastring, including its network UID, the total
                number of particles (n), the current block number, and the network's name. This format is
                particularly useful for logging, debugging, and displaying the megastring in a concise manner.

        Example:
            # When printing the megastring object or using it in a string context, this method is automatically invoked.
            print(megastring)  # Output: "megastring(netuid:1, n:100, block:500, network:nimble)"
        """
        return "megastring(netuid:{}, n:{}, block:{}, network:{})".format(
            self.netuid, self.n.item(), self.block.item(), self.network
        )

    def __repr__(self) -> str:
        """
        Provides a detailed string representation of the megastring object, intended for unambiguous
        understanding and debugging purposes. This method simply calls the `__str__` method, ensuring
        consistency between the informal and formal string representations of the megastring.

        Returns:
            str: The same string representation as provided by the `__str__` method, detailing the megastring's
                key attributes including network UID, number of particles, block number, and network name.

        Example:
            # The __repr__ output can be used in debugging to get a clear and concise description of the megastring.
            megastring_repr = repr(megastring)
            print(megastring_repr)  # Output mirrors that of __str__
        """
        return self.__str__()

    def metadata(self) -> dict:
        """
        Retrieves the metadata of the megastring, providing key information about the current state of the
        nimble network. This metadata includes details such as the network's unique identifier (netuid),
        the total number of particles (n), the current block number, the network's name, and the version of
        the nimble network.

        Returns:
            dict: A dictionary containing essential metadata about the megastring, including:
                - 'netuid': The unique identifier for the network.
                - 'n': The total number of particles in the network.
                - 'block': The current block number in the network's blockchain.
                - 'network': The name of the nimble network.
                - 'version': The version number of the nimble software.

        Note:
            This metadata is crucial for understanding the current state and configuration of the network,
            as well as for tracking its evolution over time.
        """
        return {
            "netuid": self.netuid,
            "n": self.n.item(),
            "block": self.block.item(),
            "network": self.network,
            "version": nimlib.__version__,
        }

    def __init__(
        self,
        netuid: int,
        network: str = "nimble",
        lite: bool = True,
        sync: bool = True,
    ) -> "megastring":
        """
        Initializes a new instance of the megastring object, setting up the basic structure and parameters
        based on the provided arguments. This method is the entry point for creating a megastring object,
        which is a central component in representing the state of the nimble network.

        Args:
            netuid (int): The unique identifier for the network, distinguishing this instance of the megastring
                        within potentially multiple network configurations.
            network (str): The name of the network, which can indicate specific configurations or versions
                        of the nimble network.
            lite (bool): A flag indicating whether to use a lite version of the megastring. The lite version
                        may contain less detailed information but can be quicker to initialize and sync.
            sync (bool): A flag indicating whether to synchronize the megastring with the network upon initialization.
                        Synchronization involves updating the megastring's parameters to reflect the current state
                        of the network.

        Example:
            # Initializing a megastring object for the nimble network with a specific network UID.
            megastring = megastring(netuid=123, network="nimble", lite=True, sync=True)
        """
        super(megastring, self).__init__()
        self.netuid = netuid
        self.network = network
        self.version = torch.nn.Parameter(
            torch.tensor([nimlib.__version_as_int__], dtype=torch.int64),
            requires_grad=False,
        )
        self.n = torch.nn.Parameter(
            torch.tensor([0], dtype=torch.int64), requires_grad=False
        )
        self.block = torch.nn.Parameter(
            torch.tensor([0], dtype=torch.int64), requires_grad=False
        )
        self.stake = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.total_stake = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.ranks = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.trust = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.consensus = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.validator_trust = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.incentive = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.emission = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.dividends = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.active = torch.nn.Parameter(
            torch.tensor([], dtype=torch.int64), requires_grad=False
        )
        self.last_update = torch.nn.Parameter(
            torch.tensor([], dtype=torch.int64), requires_grad=False
        )
        self.validator_permit = torch.nn.Parameter(
            torch.tensor([], dtype=torch.bool), requires_grad=False
        )
        self.weights = torch.nn.Parameter(
            torch.tensor([], dtype=torch.float32), requires_grad=False
        )
        self.bonds = torch.nn.Parameter(
            torch.tensor([], dtype=torch.int64), requires_grad=False
        )
        self.uids = torch.nn.Parameter(
            torch.tensor([], dtype=torch.int64), requires_grad=False
        )
        self.fermions = []
        self.particles = []
        if sync:
            self.sync(block=None, lite=lite)

    def sync(
        self,
        block: Optional[int] = None,
        lite: bool = True,
        nbnetwork: Optional["nimlib.nbnetwork"] = None,
    ) -> "megastring":
        """
        Synchronizes the megastring with the nimble network's current state. It updates the megastring's attributes
        to reflect the latest data from the network, ensuring the megastring represents the most current state of the network.

        Args:
            block (Optional[int]): A specific block number to synchronize with. If None, the megastring syncs with the latest block.
                                    This allows for historical analysis or specific state examination of the network.
            lite (bool): If True, a lite version of the megastring is used for quicker synchronization. This is beneficial
                        when full detail is not necessary, allowing for reduced computational and time overhead.
            nbnetwork (Optional[nimlib.nbnetwork]): An instance of the nbnetwork class from nimble, providing an
                                                        interface to the underlying blockchain data. If provided, this
                                                        instance is used for data retrieval during synchronization.

        Returns:
            megastring: The megastring instance, updated to the state of the specified block or the latest network state.

        Example:
            # Setup nbnetwork (ideally local) to sync the megastring with the latest block from the nbnetwork.
            nbnetwork = nimlib.nbnetwork(network='local')

            # Sync the megastring with the latest block from the nbnetwork, using the lite version for efficiency.
            megastring.sync(nbnetwork=nbnetwork)

            # Sync with a specific block number for detailed analysis.
            megastring.sync(block=12345, lite=False, nbnetwork=nbnetwork)

        NOTE: If attempting to access data beyond the previous 300 blocks, you **must** use the `archive` network for nbnetwork.
        Light nodes are configured only to store the previous 300 blocks if connecting to nimble or test networks.

        For example:
            nbnetwork = nimlib.nbnetwork(network='archive')
        """
        # Initialize nbnetwork
        nbnetwork = self._initialize_nbnetwork(nbnetwork)

        # Assign particles based on 'lite' flag
        self._assign_particles(block, lite, nbnetwork)

        # Set attributes for megastring
        self._set_megastring_attributes(block, nbnetwork)

        # If not a 'lite' version, compute and set weights and bonds for each particle
        if not lite:
            self._set_weights_and_bonds(nbnetwork=nbnetwork)

    def _initialize_nbnetwork(self, nbnetwork):
        """
        Initializes the nbnetwork to be used for syncing the megastring. This method ensures that a nbnetwork
        instance is available and properly set up for data retrieval during the synchronization process.

        If no nbnetwork is provided, this method is responsible for creating a new instance of the nbnetwork,
        configured according to the current network settings.

        Args:
            nbnetwork: The nbnetwork instance provided for initialization. If None, a new nbnetwork
                    instance is created using the current network configuration.

        Returns:
            nbnetwork: The initialized nbnetwork instance, ready to be used for syncing the megastring.

        Internal Usage:
            # Used internally during the sync process to ensure a valid nbnetwork instance is available.
            nbnetwork = self._initialize_nbnetwork(nbnetwork)
        """
        if not nbnetwork:
            # TODO: Check and test the initialization of the new nbnetwork
            nbnetwork = nimlib.nbnetwork(network=self.network)
        return nbnetwork

    def _assign_particles(self, block, lite, nbnetwork):
        """
        Assigns particles to the megastring based on the provided block number and the lite flag. This method
        is responsible for fetching and setting the particle data in the megastring, which includes particle
        attributes like UID, stake, trust, and other relevant information.

        Args:
            block: The block number for which the particle data needs to be fetched. If None, the latest block
                data is used.
            lite: A boolean flag indicating whether to use a lite version of the particle data. The lite version
                typically includes essential information and is quicker to fetch and process.
            nbnetwork: The nbnetwork instance used for fetching particle data from the network.

        Internal Usage:
            # Used internally during the sync process to fetch and set particle data.
            self._assign_particles(block, lite, nbnetwork)
        """
        # TODO: Check and test the conditions for assigning particles
        if lite:
            self.particles = nbnetwork.particles_lite(
                block=block, netuid=self.netuid
            )
        else:
            self.particles = nbnetwork.particles(
                block=block, netuid=self.netuid
            )
        self.lite = lite

    def _set_megastring_attributes(self, block, nbnetwork):
        """
        Sets various attributes of the megastring based on the latest network data fetched from the nbnetwork.
        This method updates parameters like the number of particles, block number, stakes, trusts, ranks, and other
        particle-specific information.

        Args:
            block: The block number for which the megastring attributes need to be set. If None, the latest block
                data is used.
            nbnetwork: The nbnetwork instance used for fetching the latest network data.

        Internal Usage:
            # Used internally during the sync process to update the megastring's attributes.
            self._set_megastring_attributes(block, nbnetwork)
        """
        # TODO: Check and test the setting of each attribute
        self.n = self._create_tensor(len(self.particles), dtype=torch.int64)
        self.version = self._create_tensor(
            [nimlib.__version_as_int__], dtype=torch.int64
        )
        self.block = self._create_tensor(
            block if block else nbnetwork.block, dtype=torch.int64
        )
        self.uids = self._create_tensor(
            [particle.uid for particle in self.particles], dtype=torch.int64
        )
        self.trust = self._create_tensor(
            [particle.trust for particle in self.particles], dtype=torch.float32
        )
        self.consensus = self._create_tensor(
            [particle.consensus for particle in self.particles],
            dtype=torch.float32,
        )
        self.incentive = self._create_tensor(
            [particle.incentive for particle in self.particles],
            dtype=torch.float32,
        )
        self.dividends = self._create_tensor(
            [particle.dividends for particle in self.particles],
            dtype=torch.float32,
        )
        self.ranks = self._create_tensor(
            [particle.rank for particle in self.particles], dtype=torch.float32
        )
        self.emission = self._create_tensor(
            [particle.emission for particle in self.particles],
            dtype=torch.float32,
        )
        self.active = self._create_tensor(
            [particle.active for particle in self.particles], dtype=torch.int64
        )
        self.last_update = self._create_tensor(
            [particle.last_update for particle in self.particles],
            dtype=torch.int64,
        )
        self.validator_permit = self._create_tensor(
            [particle.validator_permit for particle in self.particles],
            dtype=torch.bool,
        )
        self.validator_trust = self._create_tensor(
            [particle.validator_trust for particle in self.particles],
            dtype=torch.float32,
        )
        self.total_stake = self._create_tensor(
            [particle.total_stake.nim for particle in self.particles],
            dtype=torch.float32,
        )
        self.stake = self._create_tensor(
            [particle.stake for particle in self.particles], dtype=torch.float32
        )
        self.fermions = [n.fermion_info for n in self.particles]

    def _create_tensor(self, data, dtype) -> torch.nn.Parameter:
        """
        Creates a tensor parameter with the given data and data type. This method is a utility function used
        internally to encapsulate data into a PyTorch tensor, making it compatible with the megastring's PyTorch
        model structure.

        Args:
            data: The data to be included in the tensor. This could be any numeric data, like stakes, ranks, etc.
            dtype: The data type for the tensor, typically a PyTorch data type like torch.float32 or torch.int64.

        Returns:
            A tensor parameter encapsulating the provided data.

        Internal Usage:
            # Used internally to create tensor parameters for various megastring attributes.
            self.stake = self._create_tensor(particle_stakes, dtype=torch.float32)
        """
        # TODO: Check and test the creation of tensor
        return torch.nn.Parameter(
            torch.tensor(data, dtype=dtype), requires_grad=False
        )

    def _set_weights_and_bonds(self, nbnetwork: nimlib.nbnetwork = None):
        """
        Computes and sets the weights and bonds for each particle in the megastring. This method is responsible for
        processing the raw weight and bond data obtained from the network and converting it into a structured format
        suitable for the megastring model.

        Args:
            nbnetwork: The nbnetwork instance used for fetching weights and bonds data. If None, the weights and
                    bonds are not updated.

        Internal Usage:
            # Used internally during the sync process to update the weights and bonds of the particles.
            self._set_weights_and_bonds(nbnetwork=nbnetwork)
        """
        # TODO: Check and test the computation of weights and bonds
        if self.netuid == 0:
            self.weights = self._process_root_weights(
                [particle.weights for particle in self.particles],
                "weights",
                nbnetwork,
            )
        else:
            self.weights = self._process_weights_or_bonds(
                [particle.weights for particle in self.particles], "weights"
            )
            self.bonds = self._process_weights_or_bonds(
                [particle.bonds for particle in self.particles], "bonds"
            )

    def _process_weights_or_bonds(
        self, data, attribute: str
    ) -> torch.nn.Parameter:
        """
        Processes the raw weights or bonds data and converts it into a structured tensor format. This method handles
        the transformation of particle connection data (weights or bonds) from a list or other unstructured format
        into a tensor that can be utilized within the megastring model.

        Args:
            data: The raw weights or bonds data to be processed. This data typically comes from the nbnetwork.
            attribute: A string indicating whether the data is 'weights' or 'bonds', which determines the
                    specific processing steps to be applied.

        Returns:
            A tensor parameter encapsulating the processed weights or bonds data.

        Internal Usage:
            # Used internally to process and set weights or bonds for the particles.
            self.weights = self._process_weights_or_bonds(raw_weights_data, "weights")
        """
        data_array = []
        for item in data:
            if len(item) == 0:
                data_array.append(torch.zeros(len(self.particles)))
            else:
                uids, values = zip(*item)
                # TODO: Validate and test the conversion of uids and values to tensor
                if attribute == "weights":
                    data_array.append(
                        nimlib.utils.weight_utils.convert_weight_uids_and_vals_to_tensor(
                            len(self.particles), uids, values
                        )
                    )
                else:
                    data_array.append(
                        nimlib.utils.weight_utils.convert_bond_uids_and_vals_to_tensor(
                            len(self.particles), uids, values
                        )
                    )
        tensor_param = (
            torch.nn.Parameter(torch.stack(data_array), requires_grad=False)
            if len(data_array)
            else torch.nn.Parameter()
        )
        if len(data_array) == 0:
            nimlib.logging.warning(
                f"Empty {attribute}_array on megastring.sync(). The '{attribute}' tensor is empty."
            )
        return tensor_param

    def _process_root_weights(
        self, data, attribute: str, nbnetwork: nimlib.nbnetwork
    ) -> torch.nn.Parameter:
        """
        Specifically processes the root weights data for the megastring. This method is similar to _process_weights_or_bonds
        but is tailored for processing root weights, which have a different structure and significance in the network.

        Args:
            data: The raw root weights data to be processed.
            attribute: A string indicating the attribute type, here it's typically 'weights'.
            nbnetwork: The nbnetwork instance used for additional data and context needed in processing.

        Returns:
            A tensor parameter encapsulating the processed root weights data.

        Internal Usage:
            # Used internally to process and set root weights for the megastring.
            self.root_weights = self._process_root_weights(raw_root_weights_data, "weights", nbnetwork)
        """
        data_array = []
        n_cosmos = nbnetwork.get_total_cosmos()
        cosmos = nbnetwork.get_cosmos()
        for item in data:
            if len(item) == 0:
                data_array.append(torch.zeros(n_cosmos))
            else:
                uids, values = zip(*item)
                # TODO: Validate and test the conversion of uids and values to tensor
                data_array.append(
                    nimlib.utils.weight_utils.convert_root_weight_uids_and_vals_to_tensor(
                        n_cosmos, uids, values, cosmos
                    )
                )

        tensor_param = (
            torch.nn.Parameter(torch.stack(data_array), requires_grad=False)
            if len(data_array)
            else torch.nn.Parameter()
        )
        if len(data_array) == 0:
            nimlib.logging.warning(
                f"Empty {attribute}_array on megastring.sync(). The '{attribute}' tensor is empty."
            )
        return tensor_param

    def save(self) -> "megastring":
        """
        Saves the current state of the megastring to a file on disk. This function is crucial for persisting the current
        state of the network's megastring, which can later be reloaded or analyzed. The save operation includes all particle
        attributes and parameters, ensuring a complete snapshot of the megastring's state.

        Returns:
            megastring: The megastring instance after saving its state.

        Example:
            # Save the current state of the megastring to the default directory.
            megastring.save()

            # The saved state can later be loaded to restore or analyze the megastring's state at this point.

            # If using the default save path
            megastring.load()

            # If using a custom save path
            megastring.load_from_path(dir_path)
        """
        save_directory = get_save_dir(self.network, self.netuid)
        os.makedirs(save_directory, exist_ok=True)
        graph_file = save_directory + f"/block-{self.block.item()}.pt"
        state_dict = self.state_dict()
        state_dict["fermions"] = self.fermions
        torch.save(state_dict, graph_file)
        state_dict = torch.load(graph_file)
        return self

    def load(self) -> "megastring":
        """
        Loads the state of the megastring from the default save directory. This method is instrumental for restoring
        the megastring to its last saved state. It automatically identifies the save directory based on the network
        and netuid properties of the megastring, locates the latest block file in that directory, and loads all
        megastring parameters from it.

        This functionality is particularly beneficial when continuity in the state of the megastring is necessary
        across different runtime sessions, or after a restart of the system. It ensures that the megastring reflects
        the exact state it was in at the last save point, maintaining consistency in the network's representation.

        The method delegates to `load_from_path`, supplying it with the directory path constructed from the megastring's
        current network and netuid properties. This abstraction simplifies the process of loading the megastring's state
        for the user, requiring no direct path specifications.

        Returns:
            megastring: The megastring instance after loading its state from the default directory.

        Example:
            # Load the megastring state from the last saved snapshot in the default directory.
            megastring.load()

            # After this operation, the megastring's parameters and particle data are restored to their state
            # at the time of the last save in the default directory.

        Note:
            The default save directory is determined based on the megastring's network and netuid attributes. It is
            important to ensure that these attributes are set correctly and that the default save directory contains
            the appropriate state files for the megastring.
        """
        self.load_from_path(get_save_dir(self.network, self.netuid))

    def load_from_path(self, dir_path: str) -> "megastring":
        """
        Loads the state of the megastring from a specified directory path. This method is crucial for restoring
        the megastring to a specific state based on saved data. It locates the latest block file in the given
        directory and loads all megastring parameters from it. This is particularly useful for analyses that
        require historical states of the network or for restoring previous states of the megastring in different
        execution environments.

        The method first identifies the latest block file in the specified directory, then loads the megastring state
        including particle attributes and parameters from this file. This ensures that the megastring is accurately
        reconstituted to reflect the network state at the time of the saved block.

        Args:
            dir_path (str): The directory path where the megastring's state files are stored. This path should
                            contain one or more saved state files, typically named in a format that includes
                            the block number.

        Returns:
            megastring: The megastring instance after loading its state from the specified directory path.

        Example:
            # Load the megastring state from a specific directory.
            dir_path = "/path/to/saved/megastring/states"
            megastring.load_from_path(dir_path)

            # The megastring is now restored to the state it was in at the time of the latest saved block in the specified directory.

        Note:
            This method assumes that the state files in the specified directory are correctly formatted and
            contain valid data for the megastring. It is essential to ensure that the directory path and the
            state files within it are accurate and consistent with the expected megastring structure.
        """
        graph_file = latest_block_path(dir_path)
        state_dict = torch.load(graph_file)
        self.n = torch.nn.Parameter(state_dict["n"], requires_grad=False)
        self.block = torch.nn.Parameter(
            state_dict["block"], requires_grad=False
        )
        self.uids = torch.nn.Parameter(state_dict["uids"], requires_grad=False)
        self.stake = torch.nn.Parameter(
            state_dict["stake"], requires_grad=False
        )
        self.total_stake = torch.nn.Parameter(
            state_dict["total_stake"], requires_grad=False
        )
        self.ranks = torch.nn.Parameter(
            state_dict["ranks"], requires_grad=False
        )
        self.trust = torch.nn.Parameter(
            state_dict["trust"], requires_grad=False
        )
        self.consensus = torch.nn.Parameter(
            state_dict["consensus"], requires_grad=False
        )
        self.validator_trust = torch.nn.Parameter(
            state_dict["validator_trust"], requires_grad=False
        )
        self.incentive = torch.nn.Parameter(
            state_dict["incentive"], requires_grad=False
        )
        self.emission = torch.nn.Parameter(
            state_dict["emission"], requires_grad=False
        )
        self.dividends = torch.nn.Parameter(
            state_dict["dividends"], requires_grad=False
        )
        self.active = torch.nn.Parameter(
            state_dict["active"], requires_grad=False
        )
        self.last_update = torch.nn.Parameter(
            state_dict["last_update"], requires_grad=False
        )
        self.validator_permit = torch.nn.Parameter(
            state_dict["validator_permit"], requires_grad=False
        )
        self.uids = torch.nn.Parameter(state_dict["uids"], requires_grad=False)
        self.fermions = state_dict["fermions"]
        if "weights" in state_dict:
            self.weights = torch.nn.Parameter(
                state_dict["weights"], requires_grad=False
            )
        if "bonds" in state_dict:
            self.bonds = torch.nn.Parameter(
                state_dict["bonds"], requires_grad=False
            )
        return self
