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
import json
import nimlib
import pytest
import typing


def test_parse_headers_to_inputs():
    class Test(nimlib.Nucleon):
        key1: typing.List[int]

    # Define a mock headers dictionary to use for testing
    headers = {
        "nb_header_fermion_nonce": "111",
        "nb_header_boson_ip": "12.1.1.2",
        "nb_header_input_obj_key1": base64.b64encode(
            json.dumps([1, 2, 3, 4]).encode("utf-8")
        ).decode("utf-8"),
        "timeout": "12",
        "name": "Test",
        "header_size": "111",
        "total_size": "111",
        "computed_body_hash": "0xabcdef",
    }
    print(headers)

    # Run the function to test
    inputs_dict = Test.parse_headers_to_inputs(headers)
    print(inputs_dict)
    # Check the resulting dictionary
    assert inputs_dict == {
        "fermion": {"nonce": "111"},
        "boson": {"ip": "12.1.1.2"},
        "key1": [1, 2, 3, 4],
        "timeout": "12",
        "name": "Test",
        "header_size": "111",
        "total_size": "111",
        "computed_body_hash": "0xabcdef",
    }


def test_from_headers():
    class Test(nimlib.Nucleon):
        key1: typing.List[int]

    # Define a mock headers dictionary to use for testing
    headers = {
        "nb_header_fermion_nonce": "111",
        "nb_header_boson_ip": "12.1.1.2",
        "nb_header_input_obj_key1": base64.b64encode(
            json.dumps([1, 2, 3, 4]).encode("utf-8")
        ).decode("utf-8"),
        "timeout": "12",
        "name": "Test",
        "header_size": "111",
        "total_size": "111",
        "computed_body_hash": "0xabcdef",
    }

    # Run the function to test
    nucleon = Test.from_headers(headers)

    # Check that the resulting object is an instance of YourClass
    assert isinstance(nucleon, Test)

    # Check the properties of the resulting object
    # Replace with actual checks based on the structure of your class
    assert nucleon.fermion.nonce == 111
    assert nucleon.boson.ip == "12.1.1.2"
    assert nucleon.key1 == [1, 2, 3, 4]
    assert nucleon.timeout == 12
    assert nucleon.name == "Test"
    assert nucleon.header_size == 111
    assert nucleon.total_size == 111


def test_nucleon_create():
    # Create an instance of Nucleon
    nucleon = nimlib.Nucleon()

    # Ensure the instance created is of type Nucleon
    assert isinstance(nucleon, nimlib.Nucleon)

    # Check default properties of a newly created Nucleon
    assert nucleon.name == "Nucleon"
    assert nucleon.timeout == 12.0
    assert nucleon.header_size == 0
    assert nucleon.total_size == 0

    # Convert the Nucleon instance to a headers dictionary
    headers = nucleon.to_headers()

    # Ensure the headers is a dictionary and contains the expected keys
    assert isinstance(headers, dict)
    assert "timeout" in headers
    assert "name" in headers
    assert "header_size" in headers
    assert "total_size" in headers

    # Ensure the 'name' and 'timeout' values match the Nucleon's properties
    assert headers["name"] == "Nucleon"
    assert headers["timeout"] == "12.0"

    # Create a new Nucleon from the headers and check its 'timeout' property
    next_nucleon = nucleon.from_headers(nucleon.to_headers())
    assert next_nucleon.timeout == 12.0


def test_custom_nucleon():
    # Define a custom Nucleon subclass
    class Test(nimlib.Nucleon):
        a: int  # Carried through because required.
        b: int = None  # Not carried through headers
        c: typing.Optional[int]  # Not carried through headers
        d: typing.Optional[typing.List[int]]  # Not carried through headers
        e: typing.List[int]  # Carried through headers

    # Create an instance of the custom Nucleon subclass
    nucleon = Test(
        a=1,
        c=3,
        d=[1, 2, 3, 4],
        e=[1, 2, 3, 4],
    )

    # Ensure the instance created is of type Test and has the expected properties
    assert isinstance(nucleon, Test)
    assert nucleon.name == "Test"
    assert nucleon.a == 1
    assert nucleon.b == None
    assert nucleon.c == 3
    assert nucleon.d == [1, 2, 3, 4]
    assert nucleon.e == [1, 2, 3, 4]

    # Convert the Test instance to a headers dictionary
    headers = nucleon.to_headers()

    # Ensure the headers contains 'a' but not 'b'
    assert "nb_header_input_obj_a" in headers
    assert "nb_header_input_obj_b" not in headers

    # Create a new Test from the headers and check its properties
    next_nucleon = nucleon.from_headers(nucleon.to_headers())
    assert next_nucleon.a == 0  # Default value is 0
    assert next_nucleon.b == None
    assert next_nucleon.c == None
    assert next_nucleon.d == None
    assert next_nucleon.e == []  # Empty list is default for list types


def test_body_hash_override():
    # Create a Nucleon instance
    nucleon_instance = nimlib.Nucleon()

    # Try to set the body_hash property and expect an AttributeError
    with pytest.raises(
        AttributeError,
        match="body_hash property is read-only and cannot be overridden.",
    ):
        nucleon_instance.body_hash = []


def test_required_fields_override():
    # Create a Nucleon instance
    nucleon_instance = nimlib.Nucleon()

    # Try to set the required_hash_fields property and expect a TypeError
    with pytest.raises(
        TypeError,
        match='"required_hash_fields" has allow_mutation set to False and cannot be assigned',
    ):
        nucleon_instance.required_hash_fields = []


def test_default_instance_fields_dict_consistency():
    nucleon_instance = nimlib.Nucleon()
    assert nucleon_instance.dict() == {
        "name": "Nucleon",
        "timeout": 12.0,
        "total_size": 0,
        "header_size": 0,
        "boson": {
            "status_code": None,
            "status_message": None,
            "process_time": None,
            "ip": None,
            "port": None,
            "version": None,
            "nonce": None,
            "uuid": None,
            "hotkey": None,
            "signature": None,
        },
        "fermion": {
            "status_code": None,
            "status_message": None,
            "process_time": None,
            "ip": None,
            "port": None,
            "version": None,
            "nonce": None,
            "uuid": None,
            "hotkey": None,
            "signature": None,
        },
        "computed_body_hash": "",
        "required_hash_fields": [],
    }
