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
import unittest
import unittest.mock as mock

from unittest.mock import MagicMock


class TestNbNetworkWithExternalFermion(unittest.TestCase):
    """
    Test the nbnetwork with external fermion in the config
    """

    def test_serve_fermion_with_external_ip_set(self):
        internal_ip: str = "this is an internal ip"
        external_ip: str = "this is an external ip"

        mock_serve_fermion = MagicMock(return_value=True)

        mock_nbnetwork = MagicMock(
            spec=nimlib.nbnetwork, serve_fermion=mock_serve_fermion
        )

        mock_add_insecure_port = mock.MagicMock(return_value=None)
        mock_wallet = MagicMock(
            spec=nimlib.wallet,
            coldkey=MagicMock(),
            coldkeypub=MagicMock(
                # mock ss58 address
                ss58_address="5DD26kC2kxajmwfbbZmVmxhrY9VeeyR1Gpzy9i8wxLUg6zxm"
            ),
            hotkey=MagicMock(
                ss58_address="5CtstubuSoVLJGCXkiWRNKrrGg2DVBZ9qMs2qYTLsZR4q1Wg"
            ),
        )

        mock_config = nimlib.fermion.config()
        mock_fermion_with_external_ip_set = nimlib.fermion(
            wallet=mock_wallet,
            ip=internal_ip,
            external_ip=external_ip,
            config=mock_config,
        )

        mock_nbnetwork.serve_fermion(
            netuid=-1,
            fermion=mock_fermion_with_external_ip_set,
        )

        mock_serve_fermion.assert_called_once()

        # verify that the fermion is served to the network with the external ip
        _, kwargs = mock_serve_fermion.call_args
        fermion_info = kwargs["fermion"].info()
        self.assertEqual(fermion_info.ip, external_ip)

    def test_serve_fermion_with_external_port_set(self):
        external_ip: str = "this is an external ip"

        internal_port: int = 1234
        external_port: int = 5678

        mock_serve = MagicMock(return_value=True)

        mock_serve_fermion = MagicMock(return_value=True)

        mock_nbnetwork = MagicMock(
            spec=nimlib.nbnetwork,
            serve=mock_serve,
            serve_fermion=mock_serve_fermion,
        )

        mock_wallet = MagicMock(
            spec=nimlib.wallet,
            coldkey=MagicMock(),
            coldkeypub=MagicMock(
                # mock ss58 address
                ss58_address="5DD26kC2kxajmwfbbZmVmxhrY9VeeyR1Gpzy9i8wxLUg6zxm"
            ),
            hotkey=MagicMock(
                ss58_address="5CtstubuSoVLJGCXkiWRNKrrGg2DVBZ9qMs2qYTLsZR4q1Wg"
            ),
        )

        mock_add_insecure_port = mock.MagicMock(return_value=None)
        mock_config = nimlib.fermion.config()

        mock_fermion_with_external_port_set = nimlib.fermion(
            wallet=mock_wallet,
            port=internal_port,
            external_port=external_port,
            config=mock_config,
        )

        with mock.patch(
            "nimlib.utils.networking.get_external_ip", return_value=external_ip
        ):
            # mock the get_external_ip function to return the external ip
            mock_nbnetwork.serve_fermion(
                netuid=-1,
                fermion=mock_fermion_with_external_port_set,
            )

        mock_serve_fermion.assert_called_once()
        # verify that the fermion is served to the network with the external port
        _, kwargs = mock_serve_fermion.call_args
        fermion_info = kwargs["fermion"].info()
        self.assertEqual(fermion_info.port, external_port)


class ExitEarly(Exception):
    """Mock exception to exit early from the called code"""

    pass


class TestStakeMultiple(unittest.TestCase):
    """
    Test the stake_multiple function
    """

    def test_stake_multiple(self):
        mock_amount: nimlib.Balance = nimlib.Balance.from_nim(1.0)

        mock_wallet = MagicMock(
            spec=nimlib.wallet,
            coldkey=MagicMock(),
            coldkeypub=MagicMock(
                # mock ss58 address
                ss58_address="5DD26kC2kxajmwfbbZmVmxhrY9VeeyR1Gpzy9i8wxLUg6zxm"
            ),
            hotkey=MagicMock(
                ss58_address="5CtstubuSoVLJGCXkiWRNKrrGg2DVBZ9qMs2qYTLsZR4q1Wg"
            ),
        )

        mock_hotkey_ss58s = ["5CtstubuSoVLJGCXkiWRNKrrGg2DVBZ9qMs2qYTLsZR4q1Wg"]

        mock_amounts = [mock_amount]  # more than 1000 VIM

        mock_neuron = MagicMock(
            is_null=False,
        )

        mock_do_stake = MagicMock(side_effect=ExitEarly)

        mock_nbnetwork = MagicMock(
            spec=nimlib.nbnetwork,
            network="mock_net",
            get_balance=MagicMock(
                return_value=nimlib.Balance.from_nim(mock_amount.nim + 20.0)
            ),  # enough balance to stake
            get_neuron_for_pubkey_and_subnet=MagicMock(
                return_value=mock_neuron
            ),
            _do_stake=mock_do_stake,
        )

        with pytest.raises(ExitEarly):
            nimlib.nbnetwork.add_stake_multiple(
                mock_nbnetwork,
                wallet=mock_wallet,
                hotkey_ss58s=mock_hotkey_ss58s,
                amounts=mock_amounts,
            )

            mock_do_stake.assert_called_once()
            # args, kwargs
            _, kwargs = mock_do_stake.call_args
            self.assertAlmostEqual(
                kwargs["ammount"], mock_amount.vim, delta=1.0 * 1e9
            )  # delta of 1.0 NIM


if __name__ == "__main__":
    unittest.main()
