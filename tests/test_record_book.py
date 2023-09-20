import pytest
from labchronicle.core import RecordBook
from labchronicle.utils import get_system_info


# Test cases for RecordBook
@pytest.fixture
def config(tmp_path):
    return {
        'handler': 'hdf5',
        'log_path': str(tmp_path / "test.hdf5"),
    }


def test_initialize_record_book_with_write_enabled(config):
    record_book = RecordBook(config, enable_write=True)
    assert record_book._enable_write is True
    system_info = get_system_info()
    assert record_book._system_info['user'] == system_info['user']


def test_create_and_load_record_book(config):
    # Create a record book and initialize it
    init_record_book = RecordBook(config, enable_write=True)
    assert init_record_book._enable_write is True

    # Create another record book that loads the previous record book
    load_record_book = RecordBook(config, enable_write=False)
    assert load_record_book._enable_write is False
    # assert other attributes if needed to ensure proper loading

    system_info = get_system_info()
    assert load_record_book._system_info['user'] == system_info['user']
