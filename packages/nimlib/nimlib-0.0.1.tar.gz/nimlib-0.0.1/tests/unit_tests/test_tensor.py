"""Unit tests for tensor.py."""
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
import base64
import msgpack
import msgpack_numpy
import nimlib
import numpy
import pytest
import torch


# This is a fixture that creates a non empty tensor for testing
@pytest.fixture
def valid_tensor():
    # Create a tensor from a list using PyTorch
    data = torch.tensor([1, 2, 3, 4])

    # Serialize the tensor into a Tensor instance and return it
    return nimlib.tensor(data)


# This is a fixture that creates an empty tensor for testing
@pytest.fixture
def empty_tensor():
    # Create a tensor from a list using PyTorch
    data = torch.tensor([])

    # Serialize the tensor into a Tensor instance and return it
    return nimlib.tensor(data)


def test_deserialize_valid(valid_tensor):
    # Deserialize the tensor from the Tensor instance
    tensor = valid_tensor.deserialize()

    # Check that the result is a PyTorch tensor with the correct values
    assert isinstance(tensor, torch.Tensor)
    assert tensor.tolist() == [1, 2, 3, 4]


def test_deserialize_empty(empty_tensor):
    # Deserialize the tensor from the Tensor instance
    tensor = empty_tensor.deserialize()

    # Check that the result is a PyTorch tensor with the correct values
    assert isinstance(tensor, torch.Tensor)
    assert tensor.tolist() == []


def test_serialize(valid_tensor):
    # Check that the serialized tensor is an instance of Tensor
    assert isinstance(valid_tensor, nimlib.Tensor)

    # The original torch tensor object
    data = torch.tensor([1, 2, 3, 4])
    torch_numpy = data.cpu().detach().numpy().copy()
    data_buffer = base64.b64encode(
        msgpack.packb(torch_numpy, default=msgpack_numpy.encode)
    ).decode("utf-8")

    # Check that the Tensor instance has the correct buffer, dtype, and shape
    assert valid_tensor.buffer == data_buffer
    assert valid_tensor.dtype == str(data.dtype)
    assert valid_tensor.shape == list(data.shape)

    # Check the Tensor instance type conversions
    assert isinstance(valid_tensor.tolist(), list)
    assert isinstance(valid_tensor.numpy(), numpy.ndarray)
    assert isinstance(valid_tensor.tensor(), torch.Tensor)


def test_buffer_field():
    # Create a Tensor instance with a specified buffer, dtype, and shape
    tensor = nimlib.Tensor(
        buffer="0x321e13edqwds231231231232131",
        dtype="torch.float32",
        shape=[3, 3],
    )

    # Check that the buffer field matches the provided value
    assert tensor.buffer == "0x321e13edqwds231231231232131"


def test_dtype_field():
    # Create a Tensor instance with a specified buffer, dtype, and shape
    tensor = nimlib.Tensor(
        buffer="0x321e13edqwds231231231232131",
        dtype="torch.float32",
        shape=[3, 3],
    )

    # Check that the dtype field matches the provided value
    assert tensor.dtype == "torch.float32"


def test_shape_field():
    # Create a Tensor instance with a specified buffer, dtype, and shape
    tensor = nimlib.Tensor(
        buffer="0x321e13edqwds231231231232131",
        dtype="torch.float32",
        shape=[3, 3],
    )

    # Check that the shape field matches the provided value
    assert tensor.shape == [3, 3]


def test_serialize_all_types():
    nimlib.tensor(torch.tensor([1], dtype=torch.float16))
    nimlib.tensor(torch.tensor([1], dtype=torch.float32))
    nimlib.tensor(torch.tensor([1], dtype=torch.float64))
    nimlib.tensor(torch.tensor([1], dtype=torch.uint8))
    nimlib.tensor(torch.tensor([1], dtype=torch.int32))
    nimlib.tensor(torch.tensor([1], dtype=torch.int64))
    nimlib.tensor(torch.tensor([1], dtype=torch.bool))


def test_serialize_all_types_equality():
    torchtensor = torch.randn([100], dtype=torch.float16)
    assert torch.all(nimlib.tensor(torchtensor).tensor() == torchtensor)

    torchtensor = torch.randn([100], dtype=torch.float32)
    assert torch.all(nimlib.tensor(torchtensor).tensor() == torchtensor)

    torchtensor = torch.randn([100], dtype=torch.float64)
    assert torch.all(nimlib.tensor(torchtensor).tensor() == torchtensor)

    torchtensor = torch.randint(255, 256, (1000,), dtype=torch.uint8)
    assert torch.all(nimlib.tensor(torchtensor).tensor() == torchtensor)

    torchtensor = torch.randint(
        2_147_483_646, 2_147_483_647, (1000,), dtype=torch.int32
    )
    assert torch.all(nimlib.tensor(torchtensor).tensor() == torchtensor)

    torchtensor = torch.randint(
        9_223_372_036_854_775_806,
        9_223_372_036_854_775_807,
        (1000,),
        dtype=torch.int64,
    )
    assert torch.all(nimlib.tensor(torchtensor).tensor() == torchtensor)

    torchtensor = torch.randn([100], dtype=torch.float32) < 0.5
    assert torch.all(nimlib.tensor(torchtensor).tensor() == torchtensor)
