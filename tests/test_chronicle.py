import pathlib

import pytest
from unittest.mock import MagicMock, patch
from labchronicle.chronicle import Chronicle

class MockChronicle(Chronicle):
    """
    A mock class for testing MockChronicle. Allows killing the singleton instance.
    """

    @classmethod
    def kill_singleton(cls):
        cls._instance = None


def test_start_log_default_name():
    ch = MockChronicle()

    with patch('labchronicle.chronicle.get_log_path', return_value=pathlib.Path("mocked_path")):
        ch.start_log()

    assert ch._active_record_book is not None
    assert ch._record_tracking_stack is not None
    assert ch._log_start_time is not None

    ch.kill_singleton()


def test_start_log_with_name():
    ch = MockChronicle()

    with patch('labchronicle.chronicle.get_log_path', return_value=pathlib.Path("mocked_path")):
        ch.start_log(name="test_log")

    assert ch._active_record_book is not None
    assert ch._record_tracking_stack is not None
    assert ch._log_start_time is not None

    ch.kill_singleton()


def test_new_record_no_active_log(caplog):
    ch = MockChronicle()

    with ch.new_record() as record:
        assert "No active log. Execution not recorded." in caplog.text
        assert record is None

    ch.kill_singleton()

def test_new_record_with_active_log():
    ch = MockChronicle()

    ch._log_start_time = MagicMock()
    ch._record_tracking_stack = [MagicMock()]
    ch._active_record_book = MagicMock()

    with ch.new_record() as record:
        assert record is not None
        record.set_name('test_record')
        record.record_metadata()
        assert ch._active_record_book.handler.add_record.called

    ch.kill_singleton()

def test_new_record_log_records_compromised(caplog):
    ch = MockChronicle()

    ch._log_start_time = MagicMock()
    ch._record_tracking_stack = []
    ch._active_record_book = MagicMock()

    with pytest.raises(ValueError, match="Log records compromised."):
        with ch.new_record():
            pass

    ch.kill_singleton()
