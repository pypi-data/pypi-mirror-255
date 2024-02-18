from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

import numpy as np

from jldc.core import iter_jsonl, load_jsonl, save_jsonl
from tests.conftest import TEST_DIRECTORY


@dataclass
class _InnerRecord:
    """Simple dataclass for testing purposes."""

    a: int
    b: int


@dataclass
class _TestRecord:
    """Simple dataclass for testing purposes."""

    text: str
    number: int
    created: datetime
    array: np.ndarray
    inner: _InnerRecord


TEST_LIST = [
    _TestRecord(
        text="Alice",
        number=1,
        created=datetime(2023, 12, 10, 3, 3, 3),
        array=np.array([1, 2, 3]),
        inner=_InnerRecord(11, 22),
    ),
    _TestRecord(
        text="Bob",
        number=2,
        created=datetime(2024, 8, 7, 2, 2, 2),
        array=np.array([4.0, 5.0, 6.0]),
        inner=_InnerRecord(33, 44),
    ),
]


def _check_record_equality(init: _TestRecord, loaded: _TestRecord):
    # check each field is equal
    assert init.text == loaded.text
    assert init.number == loaded.number
    assert init.created == loaded.created
    np.testing.assert_array_equal(init.array, loaded.array)

    # check type and value of dataclass field
    assert isinstance(init.inner, _InnerRecord)
    assert init.inner == loaded.inner


def test_save_then_load(create_directory):
    """Test the encoding/decoding cycle on a full file load."""
    test_path = f"{TEST_DIRECTORY}/test_save_then_load.jsonl"

    save_jsonl(test_path, TEST_LIST)

    loaded_list = load_jsonl(test_path, _TestRecord)
    assert isinstance(loaded_list, list)

    for init, loaded in zip(TEST_LIST, loaded_list):
        assert isinstance(loaded, _TestRecord)
        _check_record_equality(init, loaded)


def test_save_then_iter(create_directory):
    """Test the encoding/decoding cycle when loading file as iterator."""
    test_path = f"{TEST_DIRECTORY}/test_save_then_iter.jsonl"

    save_jsonl(test_path, TEST_LIST)

    loaded_iter = iter_jsonl(test_path, _TestRecord)
    assert isinstance(loaded_iter, Iterator)

    idx = 0
    for loaded in loaded_iter:
        init = TEST_LIST[idx]
        assert isinstance(loaded, _TestRecord)
        _check_record_equality(init, loaded)
        idx += 1

    assert idx == 2
