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

from random import randint
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union
from unittest.mock import MagicMock
from dataclasses import dataclass
from abc import abstractclassmethod
from collections.abc import Mapping

from hashlib import sha256
from ..wallet import wallet

from ..chain_data import (
    ParticleInfo,
    ParticleInfoLite,
    ProtonInfo,
    DelegateInfo,
    CosmosInfo,
    FermionInfo,
)
from ..errors import *
from ..nimble_network import NimbleNetwork
from ..utils import VIMPERNIM, U16_NORMALIZED_FLOAT
from ..utils.balance import Balance
from ..utils.registration import POWSolution

from typing import TypedDict


# Mock Testing Constant
__GLOBAL_MOCK_STATE__ = {}


class FermionServeCallParams(TypedDict):
    """
    Fermion serve chain call parameters.
    """

    version: int
    ip: int
    port: int
    ip_type: int
    netuid: int


class ProtonServeCallParams(TypedDict):
    """
    Proton serve chain call parameters.
    """

    version: int
    ip: int
    port: int
    ip_type: int
    netuid: int


BlockNumber = int


class InfoDict(Mapping):
    @abstractclassmethod
    def default(cls):
        raise NotImplementedError

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


@dataclass
class FermionInfoDict(InfoDict):
    block: int
    version: int
    ip: int  # integer representation of ip address
    port: int
    ip_type: int
    protocol: int
    placeholder1: int  # placeholder for future use
    placeholder2: int

    @classmethod
    def default(cls):
        return cls(
            block=0,
            version=0,
            ip=0,
            port=0,
            ip_type=0,
            protocol=0,
            placeholder1=0,
            placeholder2=0,
        )


@dataclass
class ProtonInfoDict(InfoDict):
    block: int
    version: int
    ip: int  # integer representation of ip address
    port: int
    ip_type: int

    @classmethod
    def default(cls):
        return cls(block=0, version=0, ip=0, port=0, ip_type=0)


@dataclass
class MockNbNetworkValue:
    value: Optional[Any]


class MockMapResult:
    records: Optional[List[Tuple[MockNbNetworkValue, MockNbNetworkValue]]]

    def __init__(
        self,
        records: Optional[
            List[
                Tuple[
                    Union[Any, MockNbNetworkValue],
                    Union[Any, MockNbNetworkValue],
                ]
            ]
        ] = None,
    ):
        _records = [
            (
                MockNbNetworkValue(value=record[0]),
                MockNbNetworkValue(value=record[1]),
            )
            # Make sure record is a tuple of MockNbNetworkValue (dict with value attr)
            if not (
                isinstance(record, tuple)
                and all(
                    isinstance(item, dict) and hasattr(item, "value")
                    for item in record
                )
            )
            else record
            for record in records
        ]

        self.records = _records

    def __iter__(self):
        return iter(self.records)


class MockSystemState(TypedDict):
    Account: Dict[str, Dict[int, int]]  # address -> block -> balance


class MockNbNetworkState(TypedDict):
    Rho: Dict[int, Dict[BlockNumber, int]]  # netuid -> block -> rho
    Kappa: Dict[int, Dict[BlockNumber, int]]  # netuid -> block -> kappa
    Difficulty: Dict[
        int, Dict[BlockNumber, int]
    ]  # netuid -> block -> difficulty
    ImmunityPeriod: Dict[
        int, Dict[BlockNumber, int]
    ]  # netuid -> block -> immunity_period
    ValidatorBatchSize: Dict[
        int, Dict[BlockNumber, int]
    ]  # netuid -> block -> validator_batch_size
    Active: Dict[int, Dict[BlockNumber, bool]]  # (netuid, uid), block -> active
    Stake: Dict[
        str, Dict[str, Dict[int, int]]
    ]  # (hotkey, coldkey) -> block -> stake

    Delegates: Dict[str, Dict[int, float]]  # address -> block -> delegate_take

    NetworksAdded: Dict[
        int, Dict[BlockNumber, bool]
    ]  # netuid -> block -> added


class MockChainState(TypedDict):
    System: MockSystemState
    NbNetworkModule: MockNbNetworkState


class MockNbNetwork(NimbleNetwork):
    """
    A Mock NbNetwork class for running tests.
    This should mock only methods that make queries to the chain.
    e.g. We mock `NbNetwork.query_nbnetwork` instead of all query methods.

    This class will also store a local (mock) state of the chain.
    """

    chain_state: MockChainState
    block_number: int

    @classmethod
    def reset(cls) -> None:
        __GLOBAL_MOCK_STATE__.clear()

        _ = cls()

    def setup(self) -> None:
        if (
            not hasattr(self, "chain_state")
            or getattr(self, "chain_state") is None
        ):
            self.chain_state = {
                "System": {"Account": {}},
                "Balances": {"ExistentialDeposit": {0: 500}},
                "NbNetworkModule": {
                    "NetworksAdded": {},
                    "Rho": {},
                    "Kappa": {},
                    "Difficulty": {},
                    "ImmunityPeriod": {},
                    "ValidatorBatchSize": {},
                    "ValidatorSequenceLength": {},
                    "ValidatorEpochsPerReset": {},
                    "ValidatorEpochLength": {},
                    "MaxAllowedValidators": {},
                    "MinAllowedWeights": {},
                    "MaxWeightLimit": {},
                    "SynergyScalingLawPower": {},
                    "ScalingLawPower": {},
                    "CosmosN": {},
                    "MaxAllowedUids": {},
                    "NetworkModality": {},
                    "BlocksSinceLastStep": {},
                    "Tempo": {},
                    "NetworkConnect": {},
                    "EmissionValues": {},
                    "Burn": {},
                    "Active": {},
                    "Uids": {},
                    "Keys": {},
                    "Owner": {},
                    "IsNetworkMember": {},
                    "LastUpdate": {},
                    "Rank": {},
                    "Emission": {},
                    "Incentive": {},
                    "Consensus": {},
                    "Trust": {},
                    "ValidatorTrust": {},
                    "Dividends": {},
                    "PruningScores": {},
                    "ValidatorPermit": {},
                    "Weights": {},
                    "Bonds": {},
                    "Stake": {},
                    "TotalStake": {0: 0},
                    "TotalIssuance": {0: 0},
                    "TotalHotkeyStake": {},
                    "TotalColdkeyStake": {},
                    "TxRateLimit": {0: 0},  # No limit
                    "Delegates": {},
                    "Fermions": {},
                    "Proton": {},
                    "CosmosOwner": {},
                },
            }

            self.block_number = 0

            self.network = "mock"
            self.chain_endpoint = "mock_endpoint"
            self.substrate = MagicMock()

    def __init__(self, *args, **kwargs) -> None:
        self.__dict__ = __GLOBAL_MOCK_STATE__

        if (
            not hasattr(self, "chain_state")
            or getattr(self, "chain_state") is None
        ):
            self.setup()

    def get_block_hash(self, block_id: int) -> str:
        return "0x" + sha256(str(block_id).encode()).hexdigest()[:64]

    def create_cosmos(self, netuid: int) -> None:
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["NetworksAdded"]:
            # Per Cosmos
            nbnetwork_state["Rho"][netuid] = {}
            nbnetwork_state["Rho"][netuid][0] = 10
            nbnetwork_state["Kappa"][netuid] = {}
            nbnetwork_state["Kappa"][netuid][0] = 32_767
            nbnetwork_state["Difficulty"][netuid] = {}
            nbnetwork_state["Difficulty"][netuid][0] = 10_000_000
            nbnetwork_state["ImmunityPeriod"][netuid] = {}
            nbnetwork_state["ImmunityPeriod"][netuid][0] = 4096
            nbnetwork_state["ValidatorBatchSize"][netuid] = {}
            nbnetwork_state["ValidatorBatchSize"][netuid][0] = 32
            nbnetwork_state["ValidatorSequenceLength"][netuid] = {}
            nbnetwork_state["ValidatorSequenceLength"][netuid][0] = 256
            nbnetwork_state["ValidatorEpochsPerReset"][netuid] = {}
            nbnetwork_state["ValidatorEpochsPerReset"][netuid][0] = 60
            nbnetwork_state["ValidatorEpochLength"][netuid] = {}
            nbnetwork_state["ValidatorEpochLength"][netuid][0] = 100
            nbnetwork_state["MaxAllowedValidators"][netuid] = {}
            nbnetwork_state["MaxAllowedValidators"][netuid][0] = 128
            nbnetwork_state["MinAllowedWeights"][netuid] = {}
            nbnetwork_state["MinAllowedWeights"][netuid][0] = 1024
            nbnetwork_state["MaxWeightLimit"][netuid] = {}
            nbnetwork_state["MaxWeightLimit"][netuid][0] = 1_000
            nbnetwork_state["SynergyScalingLawPower"][netuid] = {}
            nbnetwork_state["SynergyScalingLawPower"][netuid][0] = 50
            nbnetwork_state["ScalingLawPower"][netuid] = {}
            nbnetwork_state["ScalingLawPower"][netuid][0] = 50
            nbnetwork_state["CosmosN"][netuid] = {}
            nbnetwork_state["CosmosN"][netuid][0] = 0
            nbnetwork_state["MaxAllowedUids"][netuid] = {}
            nbnetwork_state["MaxAllowedUids"][netuid][0] = 4096
            nbnetwork_state["NetworkModality"][netuid] = {}
            nbnetwork_state["NetworkModality"][netuid][0] = 0
            nbnetwork_state["BlocksSinceLastStep"][netuid] = {}
            nbnetwork_state["BlocksSinceLastStep"][netuid][0] = 0
            nbnetwork_state["Tempo"][netuid] = {}
            nbnetwork_state["Tempo"][netuid][0] = 99
            # nbnetwork_state['NetworkConnect'][netuid] = {}
            # nbnetwork_state['NetworkConnect'][netuid][0] = {}
            nbnetwork_state["EmissionValues"][netuid] = {}
            nbnetwork_state["EmissionValues"][netuid][0] = 0
            nbnetwork_state["Burn"][netuid] = {}
            nbnetwork_state["Burn"][netuid][0] = 0

            # Per-UID/Hotkey

            nbnetwork_state["Uids"][netuid] = {}
            nbnetwork_state["Keys"][netuid] = {}
            nbnetwork_state["Owner"][netuid] = {}

            nbnetwork_state["LastUpdate"][netuid] = {}
            nbnetwork_state["Active"][netuid] = {}
            nbnetwork_state["Rank"][netuid] = {}
            nbnetwork_state["Emission"][netuid] = {}
            nbnetwork_state["Incentive"][netuid] = {}
            nbnetwork_state["Consensus"][netuid] = {}
            nbnetwork_state["Trust"][netuid] = {}
            nbnetwork_state["ValidatorTrust"][netuid] = {}
            nbnetwork_state["Dividends"][netuid] = {}
            nbnetwork_state["PruningScores"][netuid] = {}
            nbnetwork_state["PruningScores"][netuid][0] = {}
            nbnetwork_state["ValidatorPermit"][netuid] = {}

            nbnetwork_state["Weights"][netuid] = {}
            nbnetwork_state["Bonds"][netuid] = {}

            nbnetwork_state["Fermions"][netuid] = {}
            nbnetwork_state["Proton"][netuid] = {}

            nbnetwork_state["NetworksAdded"][netuid] = {}
            nbnetwork_state["NetworksAdded"][netuid][0] = True

        else:
            raise Exception("Cosmos already exists")

    def set_difficulty(self, netuid: int, difficulty: int) -> None:
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["NetworksAdded"]:
            raise Exception("Cosmos does not exist")

        nbnetwork_state["Difficulty"][netuid][self.block_number] = difficulty

    def _register_particle(self, netuid: int, hotkey: str, coldkey: str) -> int:
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["NetworksAdded"]:
            raise Exception("Cosmos does not exist")

        cosmos_n = self._get_most_recent_storage(
            nbnetwork_state["CosmosN"][netuid]
        )

        if cosmos_n > 0 and any(
            self._get_most_recent_storage(nbnetwork_state["Keys"][netuid][uid])
            == hotkey
            for uid in range(cosmos_n)
        ):
            # already_registered
            raise Exception("Hotkey already registered")
        else:
            # Not found
            if cosmos_n >= self._get_most_recent_storage(
                nbnetwork_state["MaxAllowedUids"][netuid]
            ):
                # Cosmos full, replace particle randomly
                uid = randint(0, cosmos_n - 1)
            else:
                # Cosmos not full, add new particle
                # Append as next uid and increment cosmos_n
                uid = cosmos_n
                nbnetwork_state["CosmosN"][netuid][self.block_number] = (
                    cosmos_n + 1
                )

            nbnetwork_state["Stake"][hotkey] = {}
            nbnetwork_state["Stake"][hotkey][coldkey] = {}
            nbnetwork_state["Stake"][hotkey][coldkey][self.block_number] = 0

            nbnetwork_state["Uids"][netuid][hotkey] = {}
            nbnetwork_state["Uids"][netuid][hotkey][self.block_number] = uid

            nbnetwork_state["Keys"][netuid][uid] = {}
            nbnetwork_state["Keys"][netuid][uid][self.block_number] = hotkey

            nbnetwork_state["Owner"][hotkey] = {}
            nbnetwork_state["Owner"][hotkey][self.block_number] = coldkey

            nbnetwork_state["Active"][netuid][uid] = {}
            nbnetwork_state["Active"][netuid][uid][self.block_number] = True

            nbnetwork_state["LastUpdate"][netuid][uid] = {}
            nbnetwork_state["LastUpdate"][netuid][uid][
                self.block_number
            ] = self.block_number

            nbnetwork_state["Rank"][netuid][uid] = {}
            nbnetwork_state["Rank"][netuid][uid][self.block_number] = 0.0

            nbnetwork_state["Emission"][netuid][uid] = {}
            nbnetwork_state["Emission"][netuid][uid][self.block_number] = 0.0

            nbnetwork_state["Incentive"][netuid][uid] = {}
            nbnetwork_state["Incentive"][netuid][uid][self.block_number] = 0.0

            nbnetwork_state["Consensus"][netuid][uid] = {}
            nbnetwork_state["Consensus"][netuid][uid][self.block_number] = 0.0

            nbnetwork_state["Trust"][netuid][uid] = {}
            nbnetwork_state["Trust"][netuid][uid][self.block_number] = 0.0

            nbnetwork_state["ValidatorTrust"][netuid][uid] = {}
            nbnetwork_state["ValidatorTrust"][netuid][uid][
                self.block_number
            ] = 0.0

            nbnetwork_state["Dividends"][netuid][uid] = {}
            nbnetwork_state["Dividends"][netuid][uid][self.block_number] = 0.0

            nbnetwork_state["PruningScores"][netuid][uid] = {}
            nbnetwork_state["PruningScores"][netuid][uid][
                self.block_number
            ] = 0.0

            nbnetwork_state["ValidatorPermit"][netuid][uid] = {}
            nbnetwork_state["ValidatorPermit"][netuid][uid][
                self.block_number
            ] = False

            nbnetwork_state["Weights"][netuid][uid] = {}
            nbnetwork_state["Weights"][netuid][uid][self.block_number] = []

            nbnetwork_state["Bonds"][netuid][uid] = {}
            nbnetwork_state["Bonds"][netuid][uid][self.block_number] = []

            nbnetwork_state["Fermions"][netuid][hotkey] = {}
            nbnetwork_state["Fermions"][netuid][hotkey][self.block_number] = {}

            nbnetwork_state["Proton"][netuid][hotkey] = {}
            nbnetwork_state["Proton"][netuid][hotkey][self.block_number] = {}

            if hotkey not in nbnetwork_state["IsNetworkMember"]:
                nbnetwork_state["IsNetworkMember"][hotkey] = {}
            nbnetwork_state["IsNetworkMember"][hotkey][netuid] = {}
            nbnetwork_state["IsNetworkMember"][hotkey][netuid][
                self.block_number
            ] = True

            return uid

    @staticmethod
    def _convert_to_balance(balance: Union["Balance", float, int]) -> "Balance":
        if isinstance(balance, float):
            balance = Balance.from_nim(balance)

        if isinstance(balance, int):
            balance = Balance.from_vim(balance)

        return balance

    def force_register_particle(
        self,
        netuid: int,
        hotkey: str,
        coldkey: str,
        stake: Union["Balance", float, int] = Balance(0),
        balance: Union["Balance", float, int] = Balance(0),
    ) -> int:
        """
        Force register a particle on the mock chain, returning the UID.
        """
        stake = self._convert_to_balance(stake)
        balance = self._convert_to_balance(balance)

        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["NetworksAdded"]:
            raise Exception("Cosmos does not exist")

        uid = self._register_particle(
            netuid=netuid, hotkey=hotkey, coldkey=coldkey
        )

        nbnetwork_state["TotalStake"][self.block_number] = (
            self._get_most_recent_storage(nbnetwork_state["TotalStake"])
            + stake.vim
        )
        nbnetwork_state["Stake"][hotkey][coldkey][self.block_number] = stake.vim

        if balance.vim > 0:
            self.force_set_balance(coldkey, balance)
        self.force_set_balance(coldkey, balance)

        return uid

    def force_set_balance(
        self,
        ss58_address: str,
        balance: Union["Balance", float, int] = Balance(0),
    ) -> Tuple[bool, Optional[str]]:
        """
        Returns:
            Tuple[bool, Optional[str]]: (success, err_msg)
        """
        balance = self._convert_to_balance(balance)

        if ss58_address not in self.chain_state["System"]["Account"]:
            self.chain_state["System"]["Account"][ss58_address] = {
                "data": {"free": {0: 0}}
            }

        old_balance = self.get_balance(ss58_address, self.block_number)
        diff = balance.vim - old_balance.vim

        # Update total issuance
        self.chain_state["NbNetworkModule"]["TotalIssuance"][
            self.block_number
        ] = (
            self._get_most_recent_storage(
                self.chain_state["NbNetworkModule"]["TotalIssuance"]
            )
            + diff
        )

        self.chain_state["System"]["Account"][ss58_address] = {
            "data": {"free": {self.block_number: balance.vim}}
        }

        return True, None

    # Alias for force_set_balance
    sudo_force_set_balance = force_set_balance

    def do_block_step(self) -> None:
        self.block_number += 1

        # Doesn't do epoch
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        for cosmos in nbnetwork_state["NetworksAdded"]:
            nbnetwork_state["BlocksSinceLastStep"][cosmos][
                self.block_number
            ] = (
                self._get_most_recent_storage(
                    nbnetwork_state["BlocksSinceLastStep"][cosmos]
                )
                + 1
            )

    def _handle_type_default(self, name: str, params: List[object]) -> object:
        defaults_mapping = {
            "TotalStake": 0,
            "TotalHotkeyStake": 0,
            "TotalColdkeyStake": 0,
            "Stake": 0,
        }

        return defaults_mapping.get(name, None)

    def query_nbnetwork(
        self,
        name: str,
        block: Optional[int] = None,
        params: Optional[List[object]] = [],
    ) -> MockNbNetworkValue:
        if block:
            if self.block_number < block:
                raise Exception("Cannot query block in the future")

        else:
            block = self.block_number

        state = self.chain_state["NbNetworkModule"][name]
        if state is not None:
            # Use prefix
            if len(params) > 0:
                while state is not None and len(params) > 0:
                    state = state.get(params.pop(0), None)
                    if state is None:
                        return SimpleNamespace(
                            value=self._handle_type_default(name, params)
                        )

            # Use block
            state_at_block = state.get(block, None)
            while state_at_block is None and block > 0:
                block -= 1
                state_at_block = self.state.get(block, None)
            if state_at_block is not None:
                return SimpleNamespace(value=state_at_block)

            return SimpleNamespace(
                value=self._handle_type_default(name, params)
            )
        else:
            return SimpleNamespace(
                value=self._handle_type_default(name, params)
            )

    def query_map_nbnetwork(
        self,
        name: str,
        block: Optional[int] = None,
        params: Optional[List[object]] = [],
    ) -> Optional[MockMapResult]:
        """
        Note: Double map requires one param
        """
        if block:
            if self.block_number < block:
                raise Exception("Cannot query block in the future")

        else:
            block = self.block_number

        state = self.chain_state["NbNetworkModule"][name]
        if state is not None:
            # Use prefix
            if len(params) > 0:
                while state is not None and len(params) > 0:
                    state = state.get(params.pop(0), None)
                    if state is None:
                        return MockMapResult([])

            # Check if single map or double map
            if len(state.keys()) == 0:
                return MockMapResult([])

            inner = list(state.values())[0]
            # Should have at least one key
            if len(inner.keys()) == 0:
                raise Exception("Invalid state")

            # Check if double map
            if isinstance(list(inner.values())[0], dict):
                # is double map
                raise ChainQueryError("Double map requires one param")

            # Iterate over each key and add value to list, max at block
            records = []
            for key in state:
                result = self._get_most_recent_storage(state[key], block)
                if result is None:
                    continue  # Skip if no result for this key at `block` or earlier

                records.append((key, result))

            return MockMapResult(records)
        else:
            return MockMapResult([])

    def query_constant(
        self, module_name: str, constant_name: str, block: Optional[int] = None
    ) -> Optional[object]:
        if block:
            if self.block_number < block:
                raise Exception("Cannot query block in the future")

        else:
            block = self.block_number

        state = self.chain_state.get(module_name, None)
        if state is not None:
            if constant_name in state:
                state = state[constant_name]
            else:
                return None

            # Use block
            state_at_block = self._get_most_recent_storage(state, block)
            if state_at_block is not None:
                return SimpleNamespace(value=state_at_block)

            return state_at_block["data"]["free"]  # Can be None
        else:
            return None

    def get_current_block(self) -> int:
        return self.block_number

    # ==== Balance RPC methods ====

    def get_balance(self, address: str, block: int = None) -> "Balance":
        if block:
            if self.block_number < block:
                raise Exception("Cannot query block in the future")

        else:
            block = self.block_number

        state = self.chain_state["System"]["Account"]
        if state is not None:
            if address in state:
                state = state[address]
            else:
                return Balance(0)

            # Use block
            balance_state = state["data"]["free"]
            state_at_block = self._get_most_recent_storage(
                balance_state, block
            )  # Can be None
            if state_at_block is not None:
                bal_as_int = state_at_block
                return Balance.from_vim(bal_as_int)
            else:
                return Balance(0)
        else:
            return Balance(0)

    def get_balances(self, block: int = None) -> Dict[str, "Balance"]:
        balances = {}
        for address in self.chain_state["System"]["Account"]:
            balances[address] = self.get_balance(address, block)

        return balances

    # ==== Particle RPC methods ====

    def particle_for_uid(
        self, uid: int, netuid: int, block: Optional[int] = None
    ) -> Optional[ParticleInfo]:
        if uid is None:
            return ParticleInfo._null_particle()

        if block:
            if self.block_number < block:
                raise Exception("Cannot query block in the future")

        else:
            block = self.block_number

        if netuid not in self.chain_state["NbNetworkModule"]["NetworksAdded"]:
            return None

        particle_info = self._particle_cosmos_exists(uid, netuid, block)
        if particle_info is None:
            return None

        else:
            return particle_info

    def particles(
        self, netuid: int, block: Optional[int] = None
    ) -> List[ParticleInfo]:
        if netuid not in self.chain_state["NbNetworkModule"]["NetworksAdded"]:
            raise Exception("Cosmos does not exist")

        particles = []
        cosmos_n = self._get_most_recent_storage(
            self.chain_state["NbNetworkModule"]["CosmosN"][netuid], block
        )
        for uid in range(cosmos_n):
            particle_info = self.particle_for_uid(uid, netuid, block)
            if particle_info is not None:
                particles.append(particle_info)

        return particles

    @staticmethod
    def _get_most_recent_storage(
        storage: Dict[BlockNumber, Any], block_number: Optional[int] = None
    ) -> Any:
        if block_number is None:
            items = list(storage.items())
            items.sort(key=lambda x: x[0], reverse=True)
            if len(items) == 0:
                return None

            return items[0][1]

        else:
            while block_number >= 0:
                if block_number in storage:
                    return storage[block_number]

                block_number -= 1

            return None

    def _get_fermion_info(
        self, netuid: int, hotkey: str, block: Optional[int] = None
    ) -> FermionInfoDict:
        # Fermions [netuid][hotkey][block_number]
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["Fermions"]:
            return FermionInfoDict.default()

        if hotkey not in nbnetwork_state["Fermions"][netuid]:
            return FermionInfoDict.default()

        result = self._get_most_recent_storage(
            nbnetwork_state["Fermions"][netuid][hotkey], block
        )
        if not result:
            return FermionInfoDict.default()

        return result

    def _get_proton_info(
        self, netuid: int, hotkey: str, block: Optional[int] = None
    ) -> ProtonInfoDict:
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["Proton"]:
            return ProtonInfoDict.default()

        if hotkey not in nbnetwork_state["Proton"][netuid]:
            return ProtonInfoDict.default()

        result = self._get_most_recent_storage(
            nbnetwork_state["Proton"][netuid][hotkey], block
        )
        if not result:
            return ProtonInfoDict.default()

        return result

    def _particle_cosmos_exists(
        self, uid: int, netuid: int, block: Optional[int] = None
    ) -> Optional[ParticleInfo]:
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["NetworksAdded"]:
            return None

        if (
            self._get_most_recent_storage(nbnetwork_state["CosmosN"][netuid])
            <= uid
        ):
            return None

        hotkey = self._get_most_recent_storage(
            nbnetwork_state["Keys"][netuid][uid]
        )
        if hotkey is None:
            return None

        fermion_info_ = self._get_fermion_info(netuid, hotkey, block)

        proton_info = self._get_proton_info(netuid, hotkey, block)

        coldkey = self._get_most_recent_storage(
            nbnetwork_state["Owner"][hotkey], block
        )
        active = self._get_most_recent_storage(
            nbnetwork_state["Active"][netuid][uid], block
        )
        rank = self._get_most_recent_storage(
            nbnetwork_state["Rank"][netuid][uid], block
        )
        emission = self._get_most_recent_storage(
            nbnetwork_state["Emission"][netuid][uid], block
        )
        incentive = self._get_most_recent_storage(
            nbnetwork_state["Incentive"][netuid][uid], block
        )
        consensus = self._get_most_recent_storage(
            nbnetwork_state["Consensus"][netuid][uid], block
        )
        trust = self._get_most_recent_storage(
            nbnetwork_state["Trust"][netuid][uid], block
        )
        validator_trust = self._get_most_recent_storage(
            nbnetwork_state["ValidatorTrust"][netuid][uid], block
        )
        dividends = self._get_most_recent_storage(
            nbnetwork_state["Dividends"][netuid][uid], block
        )
        pruning_score = self._get_most_recent_storage(
            nbnetwork_state["PruningScores"][netuid][uid], block
        )
        last_update = self._get_most_recent_storage(
            nbnetwork_state["LastUpdate"][netuid][uid], block
        )
        validator_permit = self._get_most_recent_storage(
            nbnetwork_state["ValidatorPermit"][netuid][uid], block
        )

        weights = self._get_most_recent_storage(
            nbnetwork_state["Weights"][netuid][uid], block
        )
        bonds = self._get_most_recent_storage(
            nbnetwork_state["Bonds"][netuid][uid], block
        )

        stake_dict = {
            coldkey: Balance.from_vim(
                self._get_most_recent_storage(
                    nbnetwork_state["Stake"][hotkey][coldkey], block
                )
            )
            for coldkey in nbnetwork_state["Stake"][hotkey]
        }

        stake = sum(stake_dict.values())

        weights = [[int(weight[0]), int(weight[1])] for weight in weights]
        bonds = [[int(bond[0]), int(bond[1])] for bond in bonds]
        rank = U16_NORMALIZED_FLOAT(rank)
        emission = emission / VIMPERNIM
        incentive = U16_NORMALIZED_FLOAT(incentive)
        consensus = U16_NORMALIZED_FLOAT(consensus)
        trust = U16_NORMALIZED_FLOAT(trust)
        validator_trust = U16_NORMALIZED_FLOAT(validator_trust)
        dividends = U16_NORMALIZED_FLOAT(dividends)
        proton_info = ProtonInfo.fix_decoded_values(proton_info)
        fermion_info_ = FermionInfo.from_particle_info(
            {
                "hotkey": hotkey,
                "coldkey": coldkey,
                "fermion_info": fermion_info_,
            }
        )

        particle_info = ParticleInfo(
            hotkey=hotkey,
            coldkey=coldkey,
            uid=uid,
            netuid=netuid,
            active=active,
            rank=rank,
            emission=emission,
            incentive=incentive,
            consensus=consensus,
            trust=trust,
            validator_trust=validator_trust,
            dividends=dividends,
            pruning_score=pruning_score,
            last_update=last_update,
            validator_permit=validator_permit,
            stake=stake,
            stake_dict=stake_dict,
            total_stake=stake,
            proton_info=proton_info,
            fermion_info=fermion_info_,
            weights=weights,
            bonds=bonds,
            is_null=False,
        )

        return particle_info

    def particle_for_uid_lite(
        self, uid: int, netuid: int, block: Optional[int] = None
    ) -> Optional[ParticleInfoLite]:
        if block:
            if self.block_number < block:
                raise Exception("Cannot query block in the future")

        else:
            block = self.block_number

        if netuid not in self.chain_state["NbNetworkModule"]["NetworksAdded"]:
            raise Exception("Cosmos does not exist")

        particle_info = self._particle_cosmos_exists(uid, netuid, block)
        if particle_info is None:
            return None

        else:
            particle_info_dict = particle_info.__dict__
            del particle_info
            del particle_info_dict["weights"]
            del particle_info_dict["bonds"]

            particle_info_lite = ParticleInfoLite(**particle_info_dict)
            return particle_info_lite

    def particles_lite(
        self, netuid: int, block: Optional[int] = None
    ) -> List[ParticleInfoLite]:
        if netuid not in self.chain_state["NbNetworkModule"]["NetworksAdded"]:
            raise Exception("Cosmos does not exist")

        particles = []
        cosmos_n = self._get_most_recent_storage(
            self.chain_state["NbNetworkModule"]["CosmosN"][netuid]
        )
        for uid in range(cosmos_n):
            particle_info = self.particle_for_uid_lite(uid, netuid, block)
            if particle_info is not None:
                particles.append(particle_info)

        return particles

    # Extrinsics
    def _do_delegation(
        self,
        wallet: "wallet",
        delegate_ss58: str,
        amount: "Balance",
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> bool:
        # Check if delegate
        if not self.is_hotkey_delegate(hotkey_ss58=delegate_ss58):
            raise Exception("Not a delegate")

        # do stake
        success = self._do_stake(
            wallet=wallet,
            hotkey_ss58=delegate_ss58,
            amount=amount,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
        )

        return success

    def _do_undelegation(
        self,
        wallet: "wallet",
        delegate_ss58: str,
        amount: "Balance",
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> bool:
        # Check if delegate
        if not self.is_hotkey_delegate(hotkey_ss58=delegate_ss58):
            raise Exception("Not a delegate")

        # do unstake
        self._do_unstake(
            wallet=wallet,
            hotkey_ss58=delegate_ss58,
            amount=amount,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
        )

    def _do_nominate(
        self,
        wallet: "wallet",
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> bool:
        hotkey_ss58 = wallet.hotkey.ss58_address
        coldkey_ss58 = wallet.coldkeypub.ss58_address

        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if self.is_hotkey_delegate(hotkey_ss58=hotkey_ss58):
            return True

        else:
            nbnetwork_state["Delegates"][hotkey_ss58] = {}
            nbnetwork_state["Delegates"][hotkey_ss58][
                self.block_number
            ] = 0.18  # Constant for now

            return True

    def get_transfer_fee(
        self, wallet: "wallet", dest: str, value: Union["Balance", float, int]
    ) -> "Balance":
        return Balance(700)

    def _do_transfer(
        self,
        wallet: "wallet",
        dest: str,
        transfer_balance: "Balance",
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        bal = self.get_balance(wallet.coldkeypub.ss58_address)
        dest_bal = self.get_balance(dest)
        transfer_fee = self.get_transfer_fee(wallet, dest, transfer_balance)

        existential_deposit = self.get_existential_deposit()

        if bal < transfer_balance + existential_deposit + transfer_fee:
            raise Exception("Insufficient balance")

        # Remove from the free balance
        self.chain_state["System"]["Account"][wallet.coldkeypub.ss58_address][
            "data"
        ]["free"][self.block_number] = (
            bal - transfer_balance - transfer_fee
        ).vim

        # Add to the free balance
        if dest not in self.chain_state["System"]["Account"]:
            self.chain_state["System"]["Account"][dest] = {"data": {"free": {}}}

        self.chain_state["System"]["Account"][dest]["data"]["free"][
            self.block_number
        ] = (dest_bal + transfer_balance).vim

        return True, None, None

    def _do_pow_register(
        self,
        netuid: int,
        wallet: "wallet",
        pow_result: "POWSolution",
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        # Assume pow result is valid

        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["NetworksAdded"]:
            raise Exception("Cosmos does not exist")

        self._register_particle(
            netuid=netuid,
            hotkey=wallet.hotkey.ss58_address,
            coldkey=wallet.coldkeypub.ss58_address,
        )

        return True, None

    def _do_burned_register(
        self,
        netuid: int,
        wallet: "wallet",
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        if netuid not in nbnetwork_state["NetworksAdded"]:
            raise Exception("Cosmos does not exist")

        bal = self.get_balance(wallet.coldkeypub.ss58_address)
        burn = self.burn(netuid=netuid)
        existential_deposit = self.get_existential_deposit()

        if bal < burn + existential_deposit:
            raise Exception("Insufficient funds")

        self._register_particle(
            netuid=netuid,
            hotkey=wallet.hotkey.ss58_address,
            coldkey=wallet.coldkeypub.ss58_address,
        )

        # Burn the funds
        self.chain_state["System"]["Account"][wallet.coldkeypub.ss58_address][
            "data"
        ]["free"][self.block_number] = (bal - burn).vim

        return True, None

    def _do_stake(
        self,
        wallet: "wallet",
        hotkey_ss58: str,
        amount: "Balance",
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> bool:
        nbnetwork_state = self.chain_state["NbNetworkModule"]

        bal = self.get_balance(wallet.coldkeypub.ss58_address)
        curr_stake = self.get_stake_for_coldkey_and_hotkey(
            hotkey_ss58=hotkey_ss58, coldkey_ss58=wallet.coldkeypub.ss58_address
        )
        if curr_stake is None:
            curr_stake = Balance(0)
        existential_deposit = self.get_existential_deposit()

        if bal < amount + existential_deposit:
            raise Exception("Insufficient funds")

        stake_state = nbnetwork_state["Stake"]

        # Stake the funds
        if not hotkey_ss58 in stake_state:
            stake_state[hotkey_ss58] = {}
        if not wallet.coldkeypub.ss58_address in stake_state[hotkey_ss58]:
            stake_state[hotkey_ss58][wallet.coldkeypub.ss58_address] = {}

        stake_state[hotkey_ss58][wallet.coldkeypub.ss58_address][
            self.block_number
        ] = amount.vim

        # Add to total_stake storage
        nbnetwork_state["TotalStake"][self.block_number] = (
            self._get_most_recent_storage(nbnetwork_state["TotalStake"])
            + amount.vim
        )

        total_hotkey_stake_state = nbnetwork_state["TotalHotkeyStake"]
        if not hotkey_ss58 in total_hotkey_stake_state:
            total_hotkey_stake_state[hotkey_ss58] = {}

        total_coldkey_stake_state = nbnetwork_state["TotalColdkeyStake"]
        if not wallet.coldkeypub.ss58_address in total_coldkey_stake_state:
            total_coldkey_stake_state[wallet.coldkeypub.ss58_address] = {}

        curr_total_hotkey_stake = self.query_nbnetwork(
            name="TotalHotkeyStake",
            params=[hotkey_ss58],
            block=min(self.block_number - 1, 0),
        )
        curr_total_coldkey_stake = self.query_nbnetwork(
            name="TotalColdkeyStake",
            params=[wallet.coldkeypub.ss58_address],
            block=min(self.block_number - 1, 0),
        )

        total_hotkey_stake_state[hotkey_ss58][self.block_number] = (
            curr_total_hotkey_stake.value + amount.vim
        )
        total_coldkey_stake_state[wallet.coldkeypub.ss58_address][
            self.block_number
        ] = (curr_total_coldkey_stake.value + amount.vim)

        # Remove from free balance
        self.chain_state["System"]["Account"][wallet.coldkeypub.ss58_address][
            "data"
        ]["free"][self.block_number] = (bal - amount).vim

        return True

    def _do_unstake(
        self,
        wallet: "wallet",
        hotkey_ss58: str,
        amount: "Balance",
        wait_for_inclusion: bool = True,
        wait_for_finalization: bool = False,
    ) -> bool:
        nbnetwork_state = self.chain_state["NbNetworkModule"]

        bal = self.get_balance(wallet.coldkeypub.ss58_address)
        curr_stake = self.get_stake_for_coldkey_and_hotkey(
            hotkey_ss58=hotkey_ss58, coldkey_ss58=wallet.coldkeypub.ss58_address
        )
        if curr_stake is None:
            curr_stake = Balance(0)

        if curr_stake < amount:
            raise Exception("Insufficient funds")

        stake_state = nbnetwork_state["Stake"]

        if curr_stake.vim == 0:
            return True

        # Unstake the funds
        # We know that the hotkey has stake, so we can just remove it
        stake_state[hotkey_ss58][wallet.coldkeypub.ss58_address][
            self.block_number
        ] = (curr_stake - amount).vim
        # Add to the free balance
        if (
            wallet.coldkeypub.ss58_address
            not in self.chain_state["System"]["Account"]
        ):
            self.chain_state["System"]["Account"][
                wallet.coldkeypub.ss58_address
            ] = {"data": {"free": {}}}

        # Remove from total stake storage
        nbnetwork_state["TotalStake"][self.block_number] = (
            self._get_most_recent_storage(nbnetwork_state["TotalStake"])
            - amount.vim
        )

        total_hotkey_stake_state = nbnetwork_state["TotalHotkeyStake"]
        if not hotkey_ss58 in total_hotkey_stake_state:
            total_hotkey_stake_state[hotkey_ss58] = {}
            total_hotkey_stake_state[hotkey_ss58][
                self.block_number
            ] = 0  # Shouldn't happen

        total_coldkey_stake_state = nbnetwork_state["TotalColdkeyStake"]
        if not wallet.coldkeypub.ss58_address in total_coldkey_stake_state:
            total_coldkey_stake_state[wallet.coldkeypub.ss58_address] = {}
            total_coldkey_stake_state[wallet.coldkeypub.ss58_address][
                self.block_number
            ] = amount.vim  # Shouldn't happen

        total_hotkey_stake_state[hotkey_ss58][self.block_number] = (
            self._get_most_recent_storage(
                nbnetwork_state["TotalHotkeyStake"][hotkey_ss58]
            )
            - amount.vim
        )
        total_coldkey_stake_state[wallet.coldkeypub.ss58_address][
            self.block_number
        ] = (
            self._get_most_recent_storage(
                nbnetwork_state["TotalColdkeyStake"][
                    wallet.coldkeypub.ss58_address
                ]
            )
            - amount.vim
        )

        self.chain_state["System"]["Account"][wallet.coldkeypub.ss58_address][
            "data"
        ]["free"][self.block_number] = (bal + amount).vim

        return True

    def get_delegate_by_hotkey(
        self, hotkey_ss58: str, block: Optional[int] = None
    ) -> Optional["DelegateInfo"]:
        nbnetwork_state = self.chain_state["NbNetworkModule"]

        if hotkey_ss58 not in nbnetwork_state["Delegates"]:
            return None

        newest_state = self._get_most_recent_storage(
            nbnetwork_state["Delegates"][hotkey_ss58], block
        )
        if newest_state is None:
            return None

        nom_result = []
        nominators = nbnetwork_state["Stake"][hotkey_ss58]
        for nominator in nominators:
            nom_amount = self.get_stake_for_coldkey_and_hotkey(
                hotkey_ss58=hotkey_ss58, coldkey_ss58=nominator, block=block
            )
            if nom_amount is not None and nom_amount.vim > 0:
                nom_result.append((nominator, nom_amount))

        registered_cosmos = []
        for cosmos in self.get_all_cosmos_netuids(block=block):
            uid = self.get_uid_for_hotkey_on_cosmos(
                hotkey_ss58=hotkey_ss58, netuid=cosmos, block=block
            )

            if uid is not None:
                registered_cosmos.append((cosmos, uid))

        info = DelegateInfo(
            hotkey_ss58=hotkey_ss58,
            total_stake=self.get_total_stake_for_hotkey(
                ss58_address=hotkey_ss58
            )
            or Balance(0),
            nominators=nom_result,
            owner_ss58=self.get_hotkey_owner(
                hotkey_ss58=hotkey_ss58, block=block
            ),
            take=0.18,
            validator_permits=[
                cosmos
                for cosmos, uid in registered_cosmos
                if self.particle_has_validator_permit(
                    uid=uid, netuid=cosmos, block=block
                )
            ],
            registrations=[cosmos for cosmos, _ in registered_cosmos],
            return_per_1000=Balance.from_nim(
                1234567
            ),  # Doesn't matter for mock?
            total_daily_return=Balance.from_nim(
                1234567
            ),  # Doesn't matter for mock?
        )

        return info

    def get_delegates(
        self, block: Optional[int] = None
    ) -> List["DelegateInfo"]:
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        delegates_info = []
        for hotkey in nbnetwork_state["Delegates"]:
            info = self.get_delegate_by_hotkey(hotkey_ss58=hotkey, block=block)
            if info is not None:
                delegates_info.append(info)

        return delegates_info

    def get_delegated(
        self, coldkey_ss58: str, block: Optional[int] = None
    ) -> List[Tuple["DelegateInfo", "Balance"]]:
        """Returns the list of delegates that a given coldkey is staked to."""
        delegates = self.get_delegates(block=block)

        result = []
        for delegate in delegates:
            if coldkey_ss58 in delegate.nominators:
                result.append((delegate, delegate.nominators[coldkey_ss58]))

        return result

    def get_all_cosmos_info(
        self, block: Optional[int] = None
    ) -> List[CosmosInfo]:
        nbnetwork_state = self.chain_state["NbNetworkModule"]
        result = []
        for cosmos in nbnetwork_state["NetworksAdded"]:
            info = self.get_cosmos_info(netuid=cosmos, block=block)
            if info is not None:
                result.append(info)

        return result

    def get_cosmos_info(
        self, netuid: int, block: Optional[int] = None
    ) -> Optional[CosmosInfo]:
        if not self.cosmos_exists(netuid=netuid, block=block):
            return None

        def query_cosmos_info(name: str) -> Optional[object]:
            return self.query_nbnetwork(
                name=name, block=block, params=[netuid]
            ).value

        info = CosmosInfo(
            netuid=netuid,
            rho=query_cosmos_info(name="Rho"),
            kappa=query_cosmos_info(name="Kappa"),
            difficulty=query_cosmos_info(name="Difficulty"),
            immunity_period=query_cosmos_info(name="ImmunityPeriod"),
            max_allowed_validators=query_cosmos_info(
                name="MaxAllowedValidators"
            ),
            min_allowed_weights=query_cosmos_info(name="MinAllowedWeights"),
            max_weight_limit=query_cosmos_info(name="MaxWeightLimit"),
            scaling_law_power=query_cosmos_info(name="ScalingLawPower"),
            cosmos_n=query_cosmos_info(name="CosmosN"),
            max_n=query_cosmos_info(name="MaxAllowedUids"),
            blocks_since_epoch=query_cosmos_info(name="BlocksSinceLastStep"),
            tempo=query_cosmos_info(name="Tempo"),
            modality=query_cosmos_info(name="NetworkModality"),
            connection_requirements={
                str(netuid_.value): percentile.value
                for netuid_, percentile in self.query_map_nbnetwork(
                    name="NetworkConnect", block=block, params=[netuid]
                ).records
            },
            emission_value=query_cosmos_info(name="EmissionValues"),
            burn=query_cosmos_info(name="Burn"),
            owner_ss58=query_cosmos_info(name="CosmosOwner"),
        )

        return info

    def _do_serve_proton(
        self,
        wallet: "wallet",
        call_params: "ProtonServeCallParams",
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        return True, None

    def _do_set_weights(
        self,
        wallet: "wallet",
        netuid: int,
        uids: int,
        vals: List[int],
        version_key: int,
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        return True, None

    def _do_serve_fermion(
        self,
        wallet: "wallet",
        call_params: "FermionServeCallParams",
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        return True, None
