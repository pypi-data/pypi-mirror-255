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
import pytest
import typing

from tests.helpers import _get_mock_wallet
from unittest.mock import MagicMock, Mock


class NucleonDummy(nimlib.Nucleon):
    input: int
    output: typing.Optional[int] = None


def dummy(nucleon: NucleonDummy) -> NucleonDummy:
    nucleon.output = nucleon.input + 1
    return nucleon


@pytest.fixture
def setup_boson():
    user_wallet = (
        _get_mock_wallet()
    )  # assuming nimlib.wallet() returns a wallet object
    boson_obj = nimlib.boson(user_wallet)
    return boson_obj


@pytest.fixture(scope="session")
def setup_fermion():
    fermion = nimlib.fermion()
    fermion.attach(forward_fn=dummy)
    fermion.start()
    yield fermion
    del fermion


def test_init(setup_boson):
    boson_obj = setup_boson
    assert isinstance(boson_obj, nimlib.boson)
    assert boson_obj.keypair == setup_boson.keypair


def test_str(setup_boson):
    boson_obj = setup_boson
    expected_string = "boson({})".format(setup_boson.keypair.ss58_address)
    assert str(boson_obj) == expected_string


def test_repr(setup_boson):
    boson_obj = setup_boson
    expected_string = "boson({})".format(setup_boson.keypair.ss58_address)
    assert repr(boson_obj) == expected_string


def test_close(setup_boson, setup_fermion):
    fermion = setup_fermion
    boson_obj = setup_boson
    # Query the fermion to open a session
    boson_obj.query(fermion, NucleonDummy(input=1))
    # Session should be automatically closed after query
    assert boson_obj._session == None


@pytest.mark.asyncio
async def test_aclose(setup_boson, setup_fermion):
    fermion = setup_fermion
    boson_obj = setup_boson

    # Use context manager to open an async session
    async with boson_obj:
        resp = await boson_obj(
            [fermion], NucleonDummy(input=1), deserialize=False
        )
    # Close should automatically be called on the session after context manager scope
    assert boson_obj._session == None


class AsyncMock(Mock):
    def __call__(self, *args, **kwargs):
        sup = super(AsyncMock, self)

        async def coro():
            return sup.__call__(*args, **kwargs)

        return coro()

    def __await__(self):
        return self().__await__()


def test_boson_create_wallet():
    d = nimlib.boson(_get_mock_wallet())
    d = nimlib.boson(_get_mock_wallet().hotkey)
    d = nimlib.boson(_get_mock_wallet().coldkeypub)
    assert d.__str__() == d.__repr__()


@pytest.mark.asyncio
async def test_forward_many():
    n = 10
    d = nimlib.boson(wallet=_get_mock_wallet())
    d.call = AsyncMock()
    fermions = [MagicMock() for _ in range(n)]

    resps = await d(fermions)
    assert len(resps) == n
    resp = await d(fermions[0])
    assert len([resp]) == 1

    resps = await d.forward(fermions)
    assert len(resps) == n
    resp = await d.forward(fermions[0])
    assert len([resp]) == 1


def test_pre_process_nucleon():
    d = nimlib.boson(wallet=_get_mock_wallet())
    s = nimlib.Nucleon()
    nucleon = d.preprocess_nucleon_for_request(
        target_fermion_info=nimlib.fermion(wallet=_get_mock_wallet()).info(),
        nucleon=s,
        timeout=12,
    )
    assert nucleon.timeout == 12
    assert nucleon.boson
    assert nucleon.fermion
    assert nucleon.boson.ip
    assert nucleon.boson.version
    assert nucleon.boson.nonce
    assert nucleon.boson.uuid
    assert nucleon.boson.hotkey
    assert nucleon.fermion.ip
    assert nucleon.fermion.port
    assert nucleon.fermion.hotkey
    assert nucleon.boson.signature
