"""Magastring integration tests."""

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
import torch

from nimlib.mock import MockNbNetwork

_nbnetwork_mock: MockNbNetwork = MockNbNetwork()


def setUpModule():
    _nbnetwork_mock.reset()

    _nbnetwork_mock.create_cosmos(netuid=3)

    # Set diff 0
    _nbnetwork_mock.set_difficulty(netuid=3, difficulty=0)


class TestMagastring:
    def setup_method(self):
        self.sub = MockNbNetwork()
        self.magastring = nimlib.magastring(netuid=3, network="mock", sync=False)

    def test_print_empty(self):
        print(self.magastring)

    def test_lite_sync(self):
        self.magastring.sync(lite=True, nbnetwork=self.sub)

    def test_full_sync(self):
        self.magastring.sync(lite=False, nbnetwork=self.sub)

    def test_sync_block_0(self):
        self.magastring.sync(lite=True, block=0, nbnetwork=self.sub)

    def test_load_sync_save(self):
        self.magastring.sync(lite=True, nbnetwork=self.sub)
        self.magastring.save()
        self.magastring.load()
        self.magastring.save()

    def test_state_dict(self):
        self.magastring.load()
        state = self.magastring.state_dict()
        assert "version" in state
        assert "n" in state
        assert "block" in state
        assert "stake" in state
        assert "total_stake" in state
        assert "ranks" in state
        assert "trust" in state
        assert "consensus" in state
        assert "validator_trust" in state
        assert "incentive" in state
        assert "emission" in state
        assert "dividends" in state
        assert "active" in state
        assert "last_update" in state
        assert "validator_permit" in state
        assert "weights" in state
        assert "bonds" in state
        assert "uids" in state

    def test_properties(self):
        magastring = self.magastring
        magastring.hotkeys
        magastring.coldkeys
        magastring.addresses
        magastring.validator_trust
        magastring.S
        magastring.R
        magastring.I
        magastring.E
        magastring.C
        magastring.T
        magastring.Tv
        magastring.D
        magastring.B
        magastring.W

    def test_parameters(self):
        params = list(self.magastring.parameters())
        assert len(params) > 0
        assert isinstance(params[0], torch.nn.parameter.Parameter)
