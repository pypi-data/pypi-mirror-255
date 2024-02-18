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
import torch
import nimlib

import json
from enum import Enum
from dataclasses import dataclass, asdict
from scalecodec.types import GenericCall
from typing import List, Tuple, Dict, Optional, Any, TypedDict, Union
from scalecodec.base import RuntimeConfiguration, ScaleBytes
from scalecodec.type_registry import load_type_registry_preset
from scalecodec.utils.ss58 import ss58_encode

from .utils import networking as net, U16_MAX, U16_NORMALIZED_FLOAT
from .utils.balance import Balance

custom_rpc_type_registry = {
    "types": {
        "CosmosInfo": {
            "type": "struct",
            "type_mapping": [
                ["netuid", "Compact<u16>"],
                ["rho", "Compact<u16>"],
                ["kappa", "Compact<u16>"],
                ["difficulty", "Compact<u64>"],
                ["immunity_period", "Compact<u16>"],
                ["max_allowed_validators", "Compact<u16>"],
                ["min_allowed_weights", "Compact<u16>"],
                ["max_weights_limit", "Compact<u16>"],
                ["scaling_law_power", "Compact<u16>"],
                ["cosmos_n", "Compact<u16>"],
                ["max_allowed_uids", "Compact<u16>"],
                ["blocks_since_last_step", "Compact<u64>"],
                ["tempo", "Compact<u16>"],
                ["network_modality", "Compact<u16>"],
                ["network_connect", "Vec<[u16; 2]>"],
                ["emission_values", "Compact<u64>"],
                ["burn", "Compact<u64>"],
                ["owner", "AccountId"],
            ],
        },
        "DelegateInfo": {
            "type": "struct",
            "type_mapping": [
                ["delegate_ss58", "AccountId"],
                ["take", "Compact<u16>"],
                ["nominators", "Vec<(AccountId, Compact<u64>)>"],
                ["owner_ss58", "AccountId"],
                ["registrations", "Vec<Compact<u16>>"],
                ["validator_permits", "Vec<Compact<u16>>"],
                ["return_per_1000", "Compact<u64>"],
                ["total_daily_return", "Compact<u64>"],
            ],
        },
        "ParticleInfo": {
            "type": "struct",
            "type_mapping": [
                ["hotkey", "AccountId"],
                ["coldkey", "AccountId"],
                ["uid", "Compact<u16>"],
                ["netuid", "Compact<u16>"],
                ["active", "bool"],
                ["fermion_info", "fermion_info"],
                ["proton_info", "ProtonInfo"],
                ["stake", "Vec<(AccountId, Compact<u64>)>"],
                ["rank", "Compact<u16>"],
                ["emission", "Compact<u64>"],
                ["incentive", "Compact<u16>"],
                ["consensus", "Compact<u16>"],
                ["trust", "Compact<u16>"],
                ["validator_trust", "Compact<u16>"],
                ["dividends", "Compact<u16>"],
                ["last_update", "Compact<u64>"],
                ["validator_permit", "bool"],
                ["weights", "Vec<(Compact<u16>, Compact<u16>)>"],
                ["bonds", "Vec<(Compact<u16>, Compact<u16>)>"],
                ["pruning_score", "Compact<u16>"],
            ],
        },
        "ParticleInfoLite": {
            "type": "struct",
            "type_mapping": [
                ["hotkey", "AccountId"],
                ["coldkey", "AccountId"],
                ["uid", "Compact<u16>"],
                ["netuid", "Compact<u16>"],
                ["active", "bool"],
                ["fermion_info", "fermion_info"],
                ["proton_info", "ProtonInfo"],
                ["stake", "Vec<(AccountId, Compact<u64>)>"],
                ["rank", "Compact<u16>"],
                ["emission", "Compact<u64>"],
                ["incentive", "Compact<u16>"],
                ["consensus", "Compact<u16>"],
                ["trust", "Compact<u16>"],
                ["validator_trust", "Compact<u16>"],
                ["dividends", "Compact<u16>"],
                ["last_update", "Compact<u64>"],
                ["validator_permit", "bool"],
                ["pruning_score", "Compact<u16>"],
            ],
        },
        "fermion_info": {
            "type": "struct",
            "type_mapping": [
                ["block", "u64"],
                ["version", "u32"],
                ["ip", "u128"],
                ["port", "u16"],
                ["ip_type", "u8"],
                ["protocol", "u8"],
                ["placeholder1", "u8"],
                ["placeholder2", "u8"],
            ],
        },
        "ProtonInfo": {
            "type": "struct",
            "type_mapping": [
                ["block", "u64"],
                ["version", "u32"],
                ["ip", "u128"],
                ["port", "u16"],
                ["ip_type", "u8"],
            ],
        },
        "IPInfo": {
            "type": "struct",
            "type_mapping": [
                ["ip", "Compact<u128>"],
                ["ip_type_and_protocol", "Compact<u8>"],
            ],
        },
        "StakeInfo": {
            "type": "struct",
            "type_mapping": [
                ["hotkey", "AccountId"],
                ["coldkey", "AccountId"],
                ["stake", "Compact<u64>"],
            ],
        },
        "CosmosHyperparameters": {
            "type": "struct",
            "type_mapping": [
                ["rho", "Compact<u16>"],
                ["kappa", "Compact<u16>"],
                ["immunity_period", "Compact<u16>"],
                ["min_allowed_weights", "Compact<u16>"],
                ["max_weights_limit", "Compact<u16>"],
                ["tempo", "Compact<u16>"],
                ["min_difficulty", "Compact<u64>"],
                ["max_difficulty", "Compact<u64>"],
                ["weights_version", "Compact<u64>"],
                ["weights_rate_limit", "Compact<u64>"],
                ["adjustment_interval", "Compact<u16>"],
                ["activity_cutoff", "Compact<u16>"],
                ["registration_allowed", "bool"],
                ["target_regs_per_interval", "Compact<u16>"],
                ["min_burn", "Compact<u64>"],
                ["max_burn", "Compact<u64>"],
                ["bonds_moving_avg", "Compact<u64>"],
                ["max_regs_per_block", "Compact<u16>"],
                ["serving_rate_limit", "Compact<u64>"],
                ["max_validators", "Compact<u16>"],
            ],
        },
    }
}


@dataclass
class FermionInfo:
    version: int
    ip: str
    port: int
    ip_type: int
    hotkey: str
    coldkey: str
    protocol: int = 4
    placeholder1: int = 0
    placeholder2: int = 0

    @property
    def is_serving(self) -> bool:
        """True if the endpoint is serving."""
        if self.ip == "0.0.0.0":
            return False
        else:
            return True

    def ip_str(self) -> str:
        """Return the whole ip as string"""
        return net.ip__str__(self.ip_type, self.ip, self.port)

    def __eq__(self, other: "FermionInfo"):
        if other == None:
            return False
        if (
            self.version == other.version
            and self.ip == other.ip
            and self.port == other.port
            and self.ip_type == other.ip_type
            and self.coldkey == other.coldkey
            and self.hotkey == other.hotkey
        ):
            return True
        else:
            return False

    def __str__(self):
        return "FermionInfo( {}, {}, {}, {} )".format(
            str(self.ip_str()),
            str(self.hotkey),
            str(self.coldkey),
            self.version,
        )

    def __repr__(self):
        return self.__str__()

    def to_string(self) -> str:
        """Converts the FermionInfo object to a string representation using JSON."""
        try:
            return json.dumps(asdict(self))
        except (TypeError, ValueError) as e:
            nimlib.logging.error(f"Error converting FermionInfo to string: {e}")
            return FermionInfo(0, "", 0, 0, "", "").to_string()

    @classmethod
    def from_string(cls, s: str) -> "FermionInfo":
        """Creates an FermionInfo object from its string representation using JSON."""
        try:
            data = json.loads(s)
            return cls(**data)
        except json.JSONDecodeError as e:
            nimlib.logging.error(f"Error decoding JSON: {e}")
        except TypeError as e:
            nimlib.logging.error(f"Type error: {e}")
        except ValueError as e:
            nimlib.logging.error(f"Value error: {e}")
        return FermionInfo(0, "", 0, 0, "", "")

    @classmethod
    def from_particle_info(cls, particle_info: dict) -> "FermionInfo":
        """Converts a dictionary to an fermion_info object."""
        return cls(
            version=particle_info["fermion_info"]["version"],
            ip=net.int_to_ip(int(particle_info["fermion_info"]["ip"])),
            port=particle_info["fermion_info"]["port"],
            ip_type=particle_info["fermion_info"]["ip_type"],
            hotkey=particle_info["hotkey"],
            coldkey=particle_info["coldkey"],
        )

    def to_parameter_dict(self) -> "torch.nn.ParameterDict":
        r"""Returns a torch tensor of the cosmos info."""
        return torch.nn.ParameterDict(self.__dict__)

    @classmethod
    def from_parameter_dict(
        cls, parameter_dict: "torch.nn.ParameterDict"
    ) -> "fermion_info":
        r"""Returns an fermion_info object from a torch parameter_dict."""
        return cls(**dict(parameter_dict))


class ChainDataType(Enum):
    ParticleInfo = 1
    CosmosInfo = 2
    DelegateInfo = 3
    ParticleInfoLite = 4
    DelegatedInfo = 5
    StakeInfo = 6
    IPInfo = 7
    CosmosHyperparameters = 8


# Constants
VIMPERNIM = 1e9
U16_MAX = 65535
U64_MAX = 18446744073709551615


def from_scale_encoding(
    input: Union[List[int], bytes, ScaleBytes],
    type_name: ChainDataType,
    is_vec: bool = False,
    is_option: bool = False,
) -> Optional[Dict]:
    type_string = type_name.name
    if type_name == ChainDataType.DelegatedInfo:
        # DelegatedInfo is a tuple of (DelegateInfo, Compact<u64>)
        type_string = f"({ChainDataType.DelegateInfo.name}, Compact<u64>)"
    if is_option:
        type_string = f"Option<{type_string}>"
    if is_vec:
        type_string = f"Vec<{type_string}>"

    return from_scale_encoding_using_type_string(input, type_string)


def from_scale_encoding_using_type_string(
    input: Union[List[int], bytes, ScaleBytes], type_string: str
) -> Optional[Dict]:
    if isinstance(input, ScaleBytes):
        as_scale_bytes = input
    else:
        if isinstance(input, list) and all([isinstance(i, int) for i in input]):
            vec_u8 = input
            as_bytes = bytes(vec_u8)
        elif isinstance(input, bytes):
            as_bytes = input
        else:
            raise TypeError("input must be a List[int], bytes, or ScaleBytes")

        as_scale_bytes = ScaleBytes(as_bytes)

    rpc_runtime_config = RuntimeConfiguration()
    rpc_runtime_config.update_type_registry(load_type_registry_preset("legacy"))
    rpc_runtime_config.update_type_registry(custom_rpc_type_registry)

    obj = rpc_runtime_config.create_scale_object(
        type_string, data=as_scale_bytes
    )

    return obj.decode()


# Dataclasses for chain data.
@dataclass
class ParticleInfo:
    r"""
    Dataclass for particle metadata.
    """
    hotkey: str
    coldkey: str
    uid: int
    netuid: int
    active: int
    stake: Balance
    # mapping of coldkey to amount staked to this Particle
    stake_dict: Dict[str, Balance]
    total_stake: Balance
    rank: float
    emission: float
    incentive: float
    consensus: float
    trust: float
    validator_trust: float
    dividends: float
    last_update: int
    validator_permit: bool
    weights: List[List[int]]
    bonds: List[List[int]]
    proton_info: "ProtonInfo"
    fermion_info: "FermionInfo"
    pruning_score: int
    is_null: bool = False

    @classmethod
    def fix_decoded_values(cls, particle_info_decoded: Any) -> "ParticleInfo":
        r"""Fixes the values of the ParticleInfo object."""
        particle_info_decoded["hotkey"] = ss58_encode(
            particle_info_decoded["hotkey"], nimlib.__ss58_format__
        )
        particle_info_decoded["coldkey"] = ss58_encode(
            particle_info_decoded["coldkey"], nimlib.__ss58_format__
        )
        stake_dict = {
            ss58_encode(coldkey, nimlib.__ss58_format__): Balance.from_vim(
                int(stake)
            )
            for coldkey, stake in particle_info_decoded["stake"]
        }
        particle_info_decoded["stake_dict"] = stake_dict
        particle_info_decoded["stake"] = sum(stake_dict.values())
        particle_info_decoded["total_stake"] = particle_info_decoded["stake"]
        particle_info_decoded["weights"] = [
            [int(weight[0]), int(weight[1])]
            for weight in particle_info_decoded["weights"]
        ]
        particle_info_decoded["bonds"] = [
            [int(bond[0]), int(bond[1])]
            for bond in particle_info_decoded["bonds"]
        ]
        particle_info_decoded["rank"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["rank"]
        )
        particle_info_decoded["emission"] = (
            particle_info_decoded["emission"] / VIMPERNIM
        )
        particle_info_decoded["incentive"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["incentive"]
        )
        particle_info_decoded["consensus"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["consensus"]
        )
        particle_info_decoded["trust"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["trust"]
        )
        particle_info_decoded["validator_trust"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["validator_trust"]
        )
        particle_info_decoded["dividends"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["dividends"]
        )
        particle_info_decoded["proton_info"] = ProtonInfo.fix_decoded_values(
            particle_info_decoded["proton_info"]
        )
        particle_info_decoded["fermion_info"] = FermionInfo.from_particle_info(
            particle_info_decoded
        )

        return cls(**particle_info_decoded)

    @classmethod
    def from_vec_u8(cls, vec_u8: List[int]) -> "ParticleInfo":
        r"""Returns a ParticleInfo object from a vec_u8."""
        if len(vec_u8) == 0:
            return ParticleInfo._null_particle()

        decoded = from_scale_encoding(vec_u8, ChainDataType.ParticleInfo)
        if decoded is None:
            return ParticleInfo._null_particle()

        decoded = ParticleInfo.fix_decoded_values(decoded)

        return decoded

    @classmethod
    def list_from_vec_u8(cls, vec_u8: List[int]) -> List["ParticleInfo"]:
        r"""Returns a list of ParticleInfo objects from a vec_u8."""

        decoded_list = from_scale_encoding(
            vec_u8, ChainDataType.ParticleInfo, is_vec=True
        )
        if decoded_list is None:
            return []

        decoded_list = [
            ParticleInfo.fix_decoded_values(decoded) for decoded in decoded_list
        ]
        return decoded_list

    @staticmethod
    def _null_particle() -> "ParticleInfo":
        particle = ParticleInfo(
            uid=0,
            netuid=0,
            active=0,
            stake=Balance.from_vim(0),
            stake_dict={},
            total_stake=Balance.from_vim(0),
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
            pruning_score=0,
        )
        return particle

    @classmethod
    def from_weights_bonds_and_particle_lite(
        cls,
        particle_lite: "ParticleInfoLite",
        weights_as_dict: Dict[int, List[Tuple[int, int]]],
        bonds_as_dict: Dict[int, List[Tuple[int, int]]],
    ) -> "ParticleInfo":
        n_dict = particle_lite.__dict__
        n_dict["weights"] = weights_as_dict.get(particle_lite.uid, [])
        n_dict["bonds"] = bonds_as_dict.get(particle_lite.uid, [])

        return cls(**n_dict)

    @staticmethod
    def _particle_dict_to_namespace(particle_dict) -> "ParticleInfo":
        # TODO: Legacy: remove?
        if (
            particle_dict["hotkey"]
            == "5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1eSuyUpnhM"
        ):
            return ParticleInfo._null_particle()
        else:
            particle = ParticleInfo(**particle_dict)
            particle.stake_dict = {
                hk: Balance.from_vim(stake)
                for hk, stake in particle.stake.items()
            }
            particle.stake = Balance.from_vim(particle.total_stake)
            particle.total_stake = particle.stake
            particle.rank = particle.rank / U16_MAX
            particle.trust = particle.trust / U16_MAX
            particle.consensus = particle.consensus / U16_MAX
            particle.validator_trust = particle.validator_trust / U16_MAX
            particle.incentive = particle.incentive / U16_MAX
            particle.dividends = particle.dividends / U16_MAX
            particle.emission = particle.emission / VIMPERNIM

            return particle


@dataclass
class ParticleInfoLite:
    r"""
    Dataclass for particle metadata, but without the weights and bonds.
    """
    hotkey: str
    coldkey: str
    uid: int
    netuid: int
    active: int
    stake: Balance
    # mapping of coldkey to amount staked to this Particle
    stake_dict: Dict[str, Balance]
    total_stake: Balance
    rank: float
    emission: float
    incentive: float
    consensus: float
    trust: float
    validator_trust: float
    dividends: float
    last_update: int
    validator_permit: bool
    # weights: List[List[int]]
    # bonds: List[List[int]] No weights or bonds in lite version
    proton_info: "ProtonInfo"
    fermion_info: "fermion_info"
    pruning_score: int
    is_null: bool = False

    @classmethod
    def fix_decoded_values(
        cls, particle_info_decoded: Any
    ) -> "ParticleInfoLite":
        r"""Fixes the values of the ParticleInfoLite object."""
        particle_info_decoded["hotkey"] = ss58_encode(
            particle_info_decoded["hotkey"], nimlib.__ss58_format__
        )
        particle_info_decoded["coldkey"] = ss58_encode(
            particle_info_decoded["coldkey"], nimlib.__ss58_format__
        )
        stake_dict = {
            ss58_encode(coldkey, nimlib.__ss58_format__): Balance.from_vim(
                int(stake)
            )
            for coldkey, stake in particle_info_decoded["stake"]
        }
        particle_info_decoded["stake_dict"] = stake_dict
        particle_info_decoded["stake"] = sum(stake_dict.values())
        particle_info_decoded["total_stake"] = particle_info_decoded["stake"]
        # Don't need weights and bonds in lite version
        # particle_info_decoded['weights'] = [[int(weight[0]), int(weight[1])] for weight in particle_info_decoded['weights']]
        # particle_info_decoded['bonds'] = [[int(bond[0]), int(bond[1])] for bond in particle_info_decoded['bonds']]
        particle_info_decoded["rank"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["rank"]
        )
        particle_info_decoded["emission"] = (
            particle_info_decoded["emission"] / VIMPERNIM
        )
        particle_info_decoded["incentive"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["incentive"]
        )
        particle_info_decoded["consensus"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["consensus"]
        )
        particle_info_decoded["trust"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["trust"]
        )
        particle_info_decoded["validator_trust"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["validator_trust"]
        )
        particle_info_decoded["dividends"] = U16_NORMALIZED_FLOAT(
            particle_info_decoded["dividends"]
        )
        particle_info_decoded["proton_info"] = ProtonInfo.fix_decoded_values(
            particle_info_decoded["proton_info"]
        )
        particle_info_decoded["fermion_info"] = FermionInfo.from_particle_info(
            particle_info_decoded
        )
        return cls(**particle_info_decoded)

    @classmethod
    def from_vec_u8(cls, vec_u8: List[int]) -> "ParticleInfoLite":
        r"""Returns a ParticleInfoLite object from a vec_u8."""
        if len(vec_u8) == 0:
            return ParticleInfoLite._null_particle()

        decoded = from_scale_encoding(vec_u8, ChainDataType.ParticleInfoLite)
        if decoded is None:
            return ParticleInfoLite._null_particle()

        decoded = ParticleInfoLite.fix_decoded_values(decoded)

        return decoded

    @classmethod
    def list_from_vec_u8(cls, vec_u8: List[int]) -> List["ParticleInfoLite"]:
        r"""Returns a list of ParticleInfoLite objects from a vec_u8."""

        decoded_list = from_scale_encoding(
            vec_u8, ChainDataType.ParticleInfoLite, is_vec=True
        )
        if decoded_list is None:
            return []

        decoded_list = [
            ParticleInfoLite.fix_decoded_values(decoded)
            for decoded in decoded_list
        ]
        return decoded_list

    @staticmethod
    def _null_particle() -> "ParticleInfoLite":
        particle = ParticleInfoLite(
            uid=0,
            netuid=0,
            active=0,
            stake=Balance.from_vim(0),
            stake_dict={},
            total_stake=Balance.from_vim(0),
            rank=0,
            emission=0,
            incentive=0,
            consensus=0,
            trust=0,
            validator_trust=0,
            dividends=0,
            last_update=0,
            validator_permit=False,
            # weights = [], // No weights or bonds in lite version
            # bonds = [],
            proton_info=None,
            fermion_info=None,
            is_null=True,
            coldkey="000000000000000000000000000000000000000000000000",
            hotkey="000000000000000000000000000000000000000000000000",
            pruning_score=0,
        )
        return particle

    @staticmethod
    def _particle_dict_to_namespace(particle_dict) -> "ParticleInfoLite":
        # TODO: Legacy: remove?
        if (
            particle_dict["hotkey"]
            == "5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1eSuyUpnhM"
        ):
            return ParticleInfoLite._null_particle()
        else:
            particle = ParticleInfoLite(**particle_dict)
            particle.stake = Balance.from_vim(particle.total_stake)
            particle.stake_dict = {
                hk: Balance.from_vim(stake)
                for hk, stake in particle.stake.items()
            }
            particle.total_stake = particle.stake
            particle.rank = particle.rank / U16_MAX
            particle.trust = particle.trust / U16_MAX
            particle.consensus = particle.consensus / U16_MAX
            particle.validator_trust = particle.validator_trust / U16_MAX
            particle.incentive = particle.incentive / U16_MAX
            particle.dividends = particle.dividends / U16_MAX
            particle.emission = particle.emission / VIMPERNIM

            return particle


@dataclass
class ProtonInfo:
    r"""
    Dataclass for proton info.
    """
    block: int
    version: int
    ip: str
    port: int
    ip_type: int

    @classmethod
    def fix_decoded_values(cls, proton_info_decoded: Dict) -> "ProtonInfo":
        r"""Returns a ProtonInfo object from a proton_info_decoded dictionary."""
        proton_info_decoded["ip"] = net.int_to_ip(
            int(proton_info_decoded["ip"])
        )

        return cls(**proton_info_decoded)


@dataclass
class DelegateInfo:
    r"""
    Dataclass for delegate info.
    """
    hotkey_ss58: str  # Hotkey of delegate
    total_stake: Balance  # Total stake of the delegate
    nominators: List[
        Tuple[str, Balance]
    ]  # List of nominators of the delegate and their stake
    owner_ss58: str  # Coldkey of owner
    take: float  # Take of the delegate as a percentage
    validator_permits: List[
        int
    ]  # List of cosmos that the delegate is allowed to validate on
    registrations: List[
        int
    ]  # List of cosmos that the delegate is registered on
    return_per_1000: Balance  # Return per 1000 nim of the delegate over a day
    total_daily_return: Balance  # Total daily return of the delegate

    @classmethod
    def fix_decoded_values(cls, decoded: Any) -> "DelegateInfo":
        r"""Fixes the decoded values."""

        return cls(
            hotkey_ss58=ss58_encode(
                decoded["delegate_ss58"], nimlib.__ss58_format__
            ),
            owner_ss58=ss58_encode(
                decoded["owner_ss58"], nimlib.__ss58_format__
            ),
            take=U16_NORMALIZED_FLOAT(decoded["take"]),
            nominators=[
                (
                    ss58_encode(nom[0], nimlib.__ss58_format__),
                    Balance.from_vim(nom[1]),
                )
                for nom in decoded["nominators"]
            ],
            total_stake=Balance.from_vim(
                sum([nom[1] for nom in decoded["nominators"]])
            ),
            validator_permits=decoded["validator_permits"],
            registrations=decoded["registrations"],
            return_per_1000=Balance.from_vim(decoded["return_per_1000"]),
            total_daily_return=Balance.from_vim(decoded["total_daily_return"]),
        )

    @classmethod
    def from_vec_u8(cls, vec_u8: List[int]) -> Optional["DelegateInfo"]:
        r"""Returns a DelegateInfo object from a vec_u8."""
        if len(vec_u8) == 0:
            return None

        decoded = from_scale_encoding(vec_u8, ChainDataType.DelegateInfo)

        if decoded is None:
            return None

        decoded = DelegateInfo.fix_decoded_values(decoded)

        return decoded

    @classmethod
    def list_from_vec_u8(cls, vec_u8: List[int]) -> List["DelegateInfo"]:
        r"""Returns a list of DelegateInfo objects from a vec_u8."""
        decoded = from_scale_encoding(
            vec_u8, ChainDataType.DelegateInfo, is_vec=True
        )

        if decoded is None:
            return []

        decoded = [DelegateInfo.fix_decoded_values(d) for d in decoded]

        return decoded

    @classmethod
    def delegated_list_from_vec_u8(
        cls, vec_u8: List[int]
    ) -> List[Tuple["DelegateInfo", Balance]]:
        r"""Returns a list of Tuples of DelegateInfo objects, and Balance, from a vec_u8.
        This is the list of delegates that the user has delegated to, and the amount of stake delegated.
        """
        decoded = from_scale_encoding(
            vec_u8, ChainDataType.DelegatedInfo, is_vec=True
        )

        if decoded is None:
            return []

        decoded = [
            (DelegateInfo.fix_decoded_values(d), Balance.from_vim(s))
            for d, s in decoded
        ]

        return decoded


@dataclass
class StakeInfo:
    r"""
    Dataclass for stake info.
    """
    hotkey_ss58: str  # Hotkey address
    coldkey_ss58: str  # Coldkey address
    stake: Balance  # Stake for the hotkey-coldkey pair

    @classmethod
    def fix_decoded_values(cls, decoded: Any) -> "StakeInfo":
        r"""Fixes the decoded values."""

        return cls(
            hotkey_ss58=ss58_encode(decoded["hotkey"], nimlib.__ss58_format__),
            coldkey_ss58=ss58_encode(
                decoded["coldkey"], nimlib.__ss58_format__
            ),
            stake=Balance.from_vim(decoded["stake"]),
        )

    @classmethod
    def from_vec_u8(cls, vec_u8: List[int]) -> Optional["StakeInfo"]:
        r"""Returns a StakeInfo object from a vec_u8."""
        if len(vec_u8) == 0:
            return None

        decoded = from_scale_encoding(vec_u8, ChainDataType.StakeInfo)

        if decoded is None:
            return None

        decoded = StakeInfo.fix_decoded_values(decoded)

        return decoded

    @classmethod
    def list_of_tuple_from_vec_u8(
        cls, vec_u8: List[int]
    ) -> Dict[str, List["StakeInfo"]]:
        r"""Returns a list of StakeInfo objects from a vec_u8."""
        decoded: Optional[
            List[Tuple(str, List[object])]
        ] = from_scale_encoding_using_type_string(
            input=vec_u8, type_string="Vec<(AccountId, Vec<StakeInfo>)>"
        )

        if decoded is None:
            return {}

        stake_map = {
            ss58_encode(
                address=account_id, ss58_format=nimlib.__ss58_format__
            ): [StakeInfo.fix_decoded_values(d) for d in stake_info]
            for account_id, stake_info in decoded
        }

        return stake_map

    @classmethod
    def list_from_vec_u8(cls, vec_u8: List[int]) -> List["StakeInfo"]:
        r"""Returns a list of StakeInfo objects from a vec_u8."""
        decoded = from_scale_encoding(
            vec_u8, ChainDataType.StakeInfo, is_vec=True
        )

        if decoded is None:
            return []

        decoded = [StakeInfo.fix_decoded_values(d) for d in decoded]

        return decoded


@dataclass
class CosmosInfo:
    r"""
    Dataclass for cosmos info.
    """
    netuid: int
    rho: int
    kappa: int
    difficulty: int
    immunity_period: int
    max_allowed_validators: int
    min_allowed_weights: int
    max_weight_limit: float
    scaling_law_power: float
    cosmos_n: int
    max_n: int
    blocks_since_epoch: int
    tempo: int
    modality: int
    # netuid -> topk percentile prunning score requirement (u16:MAX normalized.)
    connection_requirements: Dict[str, float]
    emission_value: float
    burn: Balance
    owner_ss58: str

    @classmethod
    def from_vec_u8(cls, vec_u8: List[int]) -> Optional["CosmosInfo"]:
        r"""Returns a CosmosInfo object from a vec_u8."""
        if len(vec_u8) == 0:
            return None

        decoded = from_scale_encoding(vec_u8, ChainDataType.CosmosInfo)

        if decoded is None:
            return None

        return CosmosInfo.fix_decoded_values(decoded)

    @classmethod
    def list_from_vec_u8(cls, vec_u8: List[int]) -> List["CosmosInfo"]:
        r"""Returns a list of CosmosInfo objects from a vec_u8."""
        decoded = from_scale_encoding(
            vec_u8, ChainDataType.CosmosInfo, is_vec=True, is_option=True
        )

        if decoded is None:
            return []

        decoded = [CosmosInfo.fix_decoded_values(d) for d in decoded]

        return decoded

    @classmethod
    def fix_decoded_values(cls, decoded: Dict) -> "CosmosInfo":
        r"""Returns a CosmosInfo object from a decoded CosmosInfo dictionary."""
        return CosmosInfo(
            netuid=decoded["netuid"],
            rho=decoded["rho"],
            kappa=decoded["kappa"],
            difficulty=decoded["difficulty"],
            immunity_period=decoded["immunity_period"],
            max_allowed_validators=decoded["max_allowed_validators"],
            min_allowed_weights=decoded["min_allowed_weights"],
            max_weight_limit=decoded["max_weights_limit"],
            scaling_law_power=decoded["scaling_law_power"],
            cosmos_n=decoded["cosmos_n"],
            max_n=decoded["max_allowed_uids"],
            blocks_since_epoch=decoded["blocks_since_last_step"],
            tempo=decoded["tempo"],
            modality=decoded["network_modality"],
            connection_requirements={
                str(int(netuid)): U16_NORMALIZED_FLOAT(int(req))
                for netuid, req in decoded["network_connect"]
            },
            emission_value=decoded["emission_values"],
            burn=Balance.from_vim(decoded["burn"]),
            owner_ss58=ss58_encode(decoded["owner"], nimlib.__ss58_format__),
        )

    def to_parameter_dict(self) -> "torch.nn.ParameterDict":
        r"""Returns a torch tensor of the cosmos info."""
        return torch.nn.ParameterDict(self.__dict__)

    @classmethod
    def from_parameter_dict(
        cls, parameter_dict: "torch.nn.ParameterDict"
    ) -> "CosmosInfo":
        r"""Returns a CosmosInfo object from a torch parameter_dict."""
        return cls(**dict(parameter_dict))


@dataclass
class CosmosHyperparameters:
    r"""
    Dataclass for cosmos hyperparameters.
    """
    rho: int
    kappa: int
    immunity_period: int
    min_allowed_weights: int
    max_weight_limit: float
    tempo: int
    min_difficulty: int
    max_difficulty: int
    weights_version: int
    weights_rate_limit: int
    adjustment_interval: int
    activity_cutoff: int
    registration_allowed: bool
    target_regs_per_interval: int
    min_burn: int
    max_burn: int
    bonds_moving_avg: int
    max_regs_per_block: int
    serving_rate_limit: int
    max_validators: int

    @classmethod
    def from_vec_u8(
        cls, vec_u8: List[int]
    ) -> Optional["CosmosHyperparameters"]:
        r"""Returns a CosmosHyperparameters object from a vec_u8."""
        if len(vec_u8) == 0:
            return None

        decoded = from_scale_encoding(
            vec_u8, ChainDataType.CosmosHyperparameters
        )

        if decoded is None:
            return None

        return CosmosHyperparameters.fix_decoded_values(decoded)

    @classmethod
    def list_from_vec_u8(
        cls, vec_u8: List[int]
    ) -> List["CosmosHyperparameters"]:
        r"""Returns a list of CosmosHyperparameters objects from a vec_u8."""
        decoded = from_scale_encoding(
            vec_u8,
            ChainDataType.CosmosHyperparameters,
            is_vec=True,
            is_option=True,
        )

        if decoded is None:
            return []

        decoded = [CosmosHyperparameters.fix_decoded_values(d) for d in decoded]

        return decoded

    @classmethod
    def fix_decoded_values(cls, decoded: Dict) -> "CosmosHyperparameters":
        r"""Returns a CosmosInfo object from a decoded CosmosInfo dictionary."""
        return CosmosHyperparameters(
            rho=decoded["rho"],
            kappa=decoded["kappa"],
            immunity_period=decoded["immunity_period"],
            min_allowed_weights=decoded["min_allowed_weights"],
            max_weight_limit=decoded["max_weights_limit"],
            tempo=decoded["tempo"],
            min_difficulty=decoded["min_difficulty"],
            max_difficulty=decoded["max_difficulty"],
            weights_version=decoded["weights_version"],
            weights_rate_limit=decoded["weights_rate_limit"],
            adjustment_interval=decoded["adjustment_interval"],
            activity_cutoff=decoded["activity_cutoff"],
            registration_allowed=decoded["registration_allowed"],
            target_regs_per_interval=decoded["target_regs_per_interval"],
            min_burn=decoded["min_burn"],
            max_burn=decoded["max_burn"],
            bonds_moving_avg=decoded["bonds_moving_avg"],
            max_regs_per_block=decoded["max_regs_per_block"],
            max_validators=decoded["max_validators"],
            serving_rate_limit=decoded["serving_rate_limit"],
        )

    def to_parameter_dict(self) -> "torch.nn.ParameterDict":
        r"""Returns a torch tensor of the cosmos hyperparameters."""
        return torch.nn.ParameterDict(self.__dict__)

    @classmethod
    def from_parameter_dict(
        cls, parameter_dict: "torch.nn.ParameterDict"
    ) -> "CosmosInfo":
        r"""Returns a CosmosHyperparameters object from a torch parameter_dict."""
        return cls(**dict(parameter_dict))


@dataclass
class IPInfo:
    r"""
    Dataclass for associated IP Info.
    """
    ip: str
    ip_type: int
    protocol: int

    def encode(self) -> Dict[str, Any]:
        r"""Returns a dictionary of the IPInfo object that can be encoded."""
        return {
            "ip": net.ip_to_int(
                self.ip
            ),  # IP type and protocol are encoded together as a u8
            "ip_type_and_protocol": ((self.ip_type << 4) + self.protocol)
            & 0xFF,
        }

    @classmethod
    def from_vec_u8(cls, vec_u8: List[int]) -> Optional["IPInfo"]:
        r"""Returns a IPInfo object from a vec_u8."""
        if len(vec_u8) == 0:
            return None

        decoded = from_scale_encoding(vec_u8, ChainDataType.IPInfo)

        if decoded is None:
            return None

        return IPInfo.fix_decoded_values(decoded)

    @classmethod
    def list_from_vec_u8(cls, vec_u8: List[int]) -> List["IPInfo"]:
        r"""Returns a list of IPInfo objects from a vec_u8."""
        decoded = from_scale_encoding(vec_u8, ChainDataType.IPInfo, is_vec=True)

        if decoded is None:
            return []

        decoded = [IPInfo.fix_decoded_values(d) for d in decoded]

        return decoded

    @classmethod
    def fix_decoded_values(cls, decoded: Dict) -> "IPInfo":
        r"""Returns a CosmosInfo object from a decoded IPInfo dictionary."""
        return IPInfo(
            ip=nimlib.utils.networking.int_to_ip(decoded["ip"]),
            ip_type=decoded["ip_type_and_protocol"] >> 4,
            protocol=decoded["ip_type_and_protocol"] & 0xF,
        )

    def to_parameter_dict(self) -> "torch.nn.ParameterDict":
        r"""Returns a torch tensor of the cosmos info."""
        return torch.nn.ParameterDict(self.__dict__)

    @classmethod
    def from_parameter_dict(
        cls, parameter_dict: "torch.nn.ParameterDict"
    ) -> "IPInfo":
        r"""Returns a IPInfo object from a torch parameter_dict."""
        return cls(**dict(parameter_dict))


# Senate / Proposal data


class ProposalVoteData(TypedDict):
    index: int
    threshold: int
    ayes: List[str]
    nays: List[str]
    end: int


ProposalCallData = GenericCall
