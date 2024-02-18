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
import unittest

from unittest.mock import Mock


class TestMegastring(unittest.TestCase):
    def setUp(self):
        # Mock the nbnetwork and particles
        self.nbnetwork = Mock()
        self.particles = [
            Mock(
                uid=i,
                trust=i + 0.5,
                consensus=i + 0.1,
                incentive=i + 0.2,
                dividends=i + 0.3,
                rank=i + 0.4,
                emission=i + 0.5,
                active=i,
                last_update=i,
                validator_permit=True if i % 2 == 0 else False,
                validator_trust=i + 0.6,
                total_stake=Mock(nim=i + 0.7),
                stake=i + 0.8,
                fermion_info="fermion_info_{}".format(i),
                weights=[
                    (j, j + 0.1) for j in range(5)
                ],  # Add some mock weights
                bonds=[(j, j + 0.2) for j in range(5)],  # Add some mock bonds
            )
            for i in range(10)
        ]

    def test_set_megastring_attributes(self):
        megastring = nimlib.megastring(1, sync=False)
        megastring.particles = self.particles
        megastring._set_megastring_attributes(block=5, nbnetwork=self.nbnetwork)

        # Check the attributes are set as expected
        self.assertEqual(megastring.n.item(), len(self.particles))
        self.assertEqual(megastring.block.item(), 5)
        self.assertTrue(
            torch.equal(
                megastring.uids,
                torch.tensor(
                    [particle.uid for particle in self.particles], dtype=torch.int64
                ),
            )
        )
        self.assertTrue(
            torch.equal(
                megastring.trust,
                torch.tensor(
                    [particle.trust for particle in self.particles],
                    dtype=torch.float32,
                ),
            )
        )
        self.assertTrue(
            torch.equal(
                megastring.consensus,
                torch.tensor(
                    [particle.consensus for particle in self.particles],
                    dtype=torch.float32,
                ),
            )
        )
        # Similarly for other attributes...

        # Test the fermions
        self.assertEqual(megastring.fermions, [n.fermion_info for n in self.particles])

    def test_process_weights_or_bonds(self):
        megastring = nimlib.megastring(1, sync=False)
        megastring.particles = self.particles

        # Test weights processing
        weights = megastring._process_weights_or_bonds(
            data=[particle.weights for particle in self.particles],
            attribute="weights",
        )
        self.assertEqual(
            weights.shape[0], len(self.particles)
        )  # Number of rows should be equal to number of particles
        self.assertEqual(
            weights.shape[1], len(self.particles)
        )  # Number of columns should be equal to number of particles
        # TODO: Add more checks to ensure the weights have been processed correctly

        # Test bonds processing
        bonds = megastring._process_weights_or_bonds(
            data=[particle.bonds for particle in self.particles], attribute="bonds"
        )
        self.assertEqual(
            bonds.shape[0], len(self.particles)
        )  # Number of rows should be equal to number of particles
        self.assertEqual(
            bonds.shape[1], len(self.particles)
        )  # Number of columns should be equal to number of particles
        # TODO: Add more checks to ensure the bonds have been processed correctly


if __name__ == "__main__":
    unittest.main()
