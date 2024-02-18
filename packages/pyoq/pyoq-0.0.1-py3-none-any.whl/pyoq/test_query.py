import unittest
from dataclasses import dataclass
from typing import Any
from unittest.mock import Mock

import pyoq


def test_attribute():
    @dataclass
    class Item:
        bar: Any

    an_item = Item(bar={"1": 2, "3": 4})

    book = Mock(author=Mock(first_name="Foo", bar={"1": 2, "3": 4}))

    assert pyoq(book, "author.first_name") == "Foo"

    assert pyoq(an_item, "bar.3") == 4

    # Without default values.
    assert pyoq(an_item, "foo.bar") is None


def test_keys():
    # Easy one.
    assert pyoq({"1": 2, "3": 4}, "3") == 4

    # With default values.
    assert pyoq({1: 2}, "3", default="A") == "A"

    # Without default values.
    assert pyoq({"1": 2, "3": 4}, "3.4") is None


def test_vector():

    dd = [{"1": 2, "3": 4}]
    assert pyoq(dd, "[0].3") == 4

    dd = {"top": {"middle": {"nested": "value"}}}
    assert pyoq(dd, "top.middle.nested.[2]") == "l"

    assert pyoq(dd, "top.middle.nested.[200]") is None

    assert pyoq("FOO", "[-1]") == "O"


def test_error():
    dd = {"top": {"middle": {"nested": "value"}}}
    with unittest.TestCase().assertRaises(ValueError):
        pyoq(dd, "top.middle.nested.[2")

    with unittest.TestCase().assertRaises(ValueError):
        assert pyoq({1: 2}, "") == {1: 2}


def test_range():
    assert pyoq("FOO", "0:2") == "FO"

    # Negative index.
    assert pyoq("FOO", "0:-1") == "FO"
