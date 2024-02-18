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

import pytest
import unittest
import nimlib
from typing import Any
from unittest import IsolatedAsyncioTestCase
from starlette.requests import Request
from unittest.mock import MagicMock
from nimlib.fermion import FermionMiddleware


def test_attach():
    # Create a mock FermionServer instance
    server = nimlib.fermion()

    # Define the Nucleon type
    class Nucleon(nimlib.Nucleon):
        pass

    # Define the functions with the correct signatures
    def forward_fn(nucleon: Nucleon) -> Any:
        pass

    def blacklist_fn(nucleon: Nucleon) -> bool:
        return True

    def priority_fn(nucleon: Nucleon) -> float:
        return 1.0

    def verify_fn(nucleon: Nucleon) -> None:
        pass

    # Test attaching with correct signatures
    server.attach(forward_fn, blacklist_fn, priority_fn, verify_fn)

    # Define functions with incorrect signatures
    def wrong_blacklist_fn(nucleon: Nucleon) -> int:
        return 1

    def wrong_priority_fn(nucleon: Nucleon) -> int:
        return 1

    def wrong_verify_fn(nucleon: Nucleon) -> bool:
        return True

    # Test attaching with incorrect signatures
    with pytest.raises(AssertionError):
        server.attach(forward_fn, wrong_blacklist_fn, priority_fn, verify_fn)

    with pytest.raises(AssertionError):
        server.attach(forward_fn, blacklist_fn, wrong_priority_fn, verify_fn)

    with pytest.raises(AssertionError):
        server.attach(forward_fn, blacklist_fn, priority_fn, wrong_verify_fn)


def test_attach():
    # Create a mock FermionServer instance
    server = nimlib.fermion()

    # Define the Nucleon type
    class Nucleon:
        pass

    # Define a class that inherits from Nucleon
    class InheritedNucleon(nimlib.Nucleon):
        pass

    # Define a function with the correct signature
    def forward_fn(nucleon: InheritedNucleon) -> Any:
        pass

    # Test attaching with correct signature and inherited class
    server.attach(forward_fn)

    # Define a class that does not inherit from Nucleon
    class NonInheritedNucleon:
        pass

    # Define a function with an argument of a class not inheriting from Nucleon
    def wrong_forward_fn(nucleon: NonInheritedNucleon) -> Any:
        pass

    # Test attaching with incorrect class inheritance
    with pytest.raises(AssertionError):
        server.attach(wrong_forward_fn)


# Mock nucleon class for testing


class FermionMock:
    def __init__(self):
        self.status_code = None
        self.forward_class_types = {}
        self.blacklist_fns = {}
        self.priority_fns = {}
        self.forward_fns = {}
        self.verify_fns = {}
        self.thread_pool = nimlib.PriorityThreadPoolExecutor(max_workers=1)


class NucleonMock(nimlib.Nucleon):
    pass


def verify_fn_pass(nucleon):
    pass


def verify_fn_fail(nucleon):
    raise Exception("Verification failed")


def blacklist_fn_pass(nucleon):
    return False, ""


def blacklist_fn_fail(nucleon):
    return True, ""


def priority_fn_pass(nucleon) -> float:
    return 0.0


def priority_fn_timeout(nucleon) -> float:
    return 2.0


@pytest.fixture
def middleware():
    # Mock FermionMiddleware instance with empty fermion object
    fermion = FermionMock()
    return FermionMiddleware(None, fermion)


@pytest.mark.asyncio
async def test_verify_pass(middleware):
    nucleon = NucleonMock()
    middleware.fermion.verify_fns = {"NucleonMock": verify_fn_pass}
    await middleware.verify(nucleon)
    assert nucleon.fermion.status_code != 401


@pytest.mark.asyncio
async def test_verify_fail(middleware):
    nucleon = NucleonMock()
    middleware.fermion.verify_fns = {"NucleonMock": verify_fn_fail}
    with pytest.raises(Exception):
        await middleware.verify(nucleon)
    assert nucleon.fermion.status_code == 401


@pytest.mark.asyncio
async def test_blacklist_pass(middleware):
    nucleon = NucleonMock()
    middleware.fermion.blacklist_fns = {"NucleonMock": blacklist_fn_pass}
    await middleware.blacklist(nucleon)
    assert nucleon.fermion.status_code != 403


@pytest.mark.asyncio
async def test_blacklist_fail(middleware):
    nucleon = NucleonMock()
    middleware.fermion.blacklist_fns = {"NucleonMock": blacklist_fn_fail}
    with pytest.raises(Exception):
        await middleware.blacklist(nucleon)
    assert nucleon.fermion.status_code == 403


@pytest.mark.asyncio
async def test_priority_pass(middleware):
    nucleon = NucleonMock()
    middleware.fermion.priority_fns = {"NucleonMock": priority_fn_pass}
    await middleware.priority(nucleon)
    assert nucleon.fermion.status_code != 408


class TestFermionMiddleware(IsolatedAsyncioTestCase):
    def setUp(self):
        # Create a mock app
        self.mock_app = MagicMock()
        # Create a mock fermion
        self.mock_fermion = MagicMock()
        self.mock_fermion.uuid = "1234"
        self.mock_fermion.forward_class_types = {
            "request_name": nimlib.Nucleon,
        }
        self.mock_fermion.wallet.hotkey.sign.return_value = bytes.fromhex(
            "aabbccdd"
        )
        # Create an instance of FermionMiddleware
        self.fermion_middleware = FermionMiddleware(self.mock_app, self.mock_fermion)
        return self.fermion_middleware

    @pytest.mark.asyncio
    async def test_preprocess(self):
        # Mock the request
        request = MagicMock(spec=Request)
        request.url.path = "/request_name"
        request.client.port = "5000"
        request.client.host = "192.168.0.1"
        request.headers = {}

        nucleon = await self.fermion_middleware.preprocess(request)

        # Check if the preprocess function fills the fermion information into the nucleon
        assert nucleon.fermion.version == str(nimlib.__version_as_int__)
        assert nucleon.fermion.uuid == "1234"
        assert nucleon.fermion.nonce is not None
        assert nucleon.fermion.status_message == "Success"
        assert nucleon.fermion.status_code == "100"
        assert nucleon.fermion.signature == "0xaabbccdd"

        # Check if the preprocess function fills the boson information into the nucleon
        assert nucleon.boson.port == "5000"
        assert nucleon.boson.ip == "192.168.0.1"

        # Check if the preprocess function sets the request name correctly
        assert nucleon.name == "request_name"


if __name__ == "__main__":
    unittest.main()
