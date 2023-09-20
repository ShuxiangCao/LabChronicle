import pytest
from unittest.mock import MagicMock, patch
import uuid
from pathlib import Path

from labchronicle.core import RecordEntry


# Mock the RecordBook and its handler
@pytest.fixture
def mock_record_book():
    mock_book = MagicMock()
    mock_book.handler = MagicMock()
    mock_book.handler.add_record = MagicMock()
    mock_book.handler.get_record_by_path = MagicMock()
    mock_book.handler.list_records = MagicMock(return_value=[])
    return mock_book


@pytest.fixture
def sample_record_entry(mock_record_book):
    return RecordEntry(
        record_book=mock_record_book,
        timestamp=1234567890,
        record_id=uuid.uuid4(),
        record_order=1,
        base_path=Path("/tmp")
    )


def test_record_entry_initialization(sample_record_entry):
    assert sample_record_entry.timestamp == 1234567890


def test_get_path(sample_record_entry):
    sample_record_entry.set_name("test_function")
    assert sample_record_entry.get_path() == Path("/tmp/1-test_function")


def test_touch_attribute(sample_record_entry):
    sample_record_entry.touch_attribute("test_attr")
    assert "test_attr" in sample_record_entry.get_recorded_attribute_names()


@patch.object(RecordEntry, "_load_from_path")
def test_initialization_with_missing_args_raises_assertion(load_mock, mock_record_book):
    with pytest.raises(AssertionError):
        RecordEntry(record_book=mock_record_book)


def test_invalid_load_from_path_raises_value_error(mock_record_book):
    with pytest.raises(ValueError):
        RecordEntry(record_book=mock_record_book, full_path=Path("/tmp/invalid"))


def test_set_name(sample_record_entry):
    sample_record_entry.set_name("my_function")
    assert sample_record_entry._name == "my_function"


def test_record_object(sample_record_entry):
    mock_loggable_object = MagicMock()
    mock_loggable_object.attr1 = "value1"
    sample_record_entry.set_name('test_function')
    sample_record_entry.set_name('test_function')
    sample_record_entry.touch_attribute("attr1")
    sample_record_entry.record_object(mock_loggable_object)
    # Note: Just check if the methods were called. Actual data saving/loading is mocked.
    sample_record_entry._record_book.handler.add_record.assert_called()


def test_record_args(sample_record_entry):
    args = [1, 2, 3]
    kwargs = {"a": "b"}
    sample_record_entry.set_name('test_function')
    sample_record_entry.set_name('test_function')
    sample_record_entry.record_args(args, kwargs)
    # Check if the methods were called with the right attributes
    sample_record_entry._record_book.handler.add_record.assert_any_call(
        sample_record_entry._get_attribute_path('__args__'), args)
    sample_record_entry._record_book.handler.add_record.assert_any_call(
        sample_record_entry._get_attribute_path('__kwargs__'), kwargs)


def test_get_object(sample_record_entry):
    mock_loggable_object = MagicMock()
    sample_record_entry.set_name('test_function')
    sample_record_entry._record_book.handler.get_record_by_path.return_value = mock_loggable_object
    assert sample_record_entry.get_object() == mock_loggable_object


def test_get_attribute_raises_assertion_for_non_recorded_attr(sample_record_entry):
    with pytest.raises(AssertionError):
        sample_record_entry.get_attribute("non_recorded_attr")


def test_get_args(sample_record_entry):
    args = [1, 2, 3]
    kwargs = {"a": "b"}
    sample_record_entry.set_name('test_function')
    sample_record_entry._record_book.handler.get_record_by_path.side_effect = [args, kwargs]
    retrieved_args, retrieved_kwargs = sample_record_entry.get_args()
    assert retrieved_args == args
    assert retrieved_kwargs == kwargs


def test_save_load_attribute(sample_record_entry):
    sample_record_entry.set_name('test_function')
    sample_record_entry.save_attribute("key", "value")
    sample_record_entry._record_book.handler.add_record.assert_called_with(
        sample_record_entry._get_attribute_path("key"), "value")
    sample_record_entry.load_attribute("key")
    sample_record_entry._record_book.handler.get_record_by_path.assert_called_with(
        sample_record_entry._get_attribute_path("key"))


def test_get_children_number(sample_record_entry):
    sample_record_entry.set_name('test_function')
    sample_record_entry._record_book.handler.list_records.return_value = ["1-child1", "2-child2", "attr1"]
    assert sample_record_entry.get_children_number() == 2


def test_get_children(sample_record_entry):
    sample_record_entry.set_name("test_function")
    sample_record_entry._record_book.handler.list_records.return_value = ["1-child1", "2-child2", "attr1"]
    children = sample_record_entry.children
    assert len(children) == 2
    for child in children:
        assert isinstance(child, RecordEntry)


def test_parent(mock_record_book):
    sample_record_entry = RecordEntry(
        record_book=mock_record_book,
        timestamp=1234567890,
        record_id=uuid.uuid4(),
        record_order=1,
        base_path=Path("/root/0-abc.edf")
    )

    sample_record_entry.set_name('test_function')
    parent = sample_record_entry.parent
    assert isinstance(parent, RecordEntry)


def test_properties(sample_record_entry):
    assert isinstance(sample_record_entry.record_id, uuid.UUID)
    assert isinstance(sample_record_entry.timestamp, int)
    assert isinstance(sample_record_entry.record_order, int)
    assert isinstance(sample_record_entry.base_path, Path)
