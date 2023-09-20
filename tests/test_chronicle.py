import pathlib

import pytest
from unittest.mock import MagicMock, patch
from labchronicle.chronicle import Chronicle


def test_start_log_default_name():
    ch = Chronicle()

    with patch('labchronicle.chronicle.get_log_path', return_value=pathlib.Path("mocked_path")):
        ch.start_log()

    assert ch._active_record_book is not None
    assert ch._record_tracking_stack is not None
    assert ch._log_start_time is not None


def test_start_log_with_name():
    ch = Chronicle()

    with patch('labchronicle.chronicle.get_log_path', return_value=pathlib.Path("mocked_path")):
        ch.start_log(name="test_log")

    assert ch._active_record_book is not None
    assert ch._record_tracking_stack is not None
    assert ch._log_start_time is not None


def test_new_record_no_active_log(caplog):
    ch = Chronicle()

    with ch.new_record() as record:
        assert "No active log. Execution not recorded." in caplog.text
        assert record is None


def test_new_record_with_active_log():
    ch = Chronicle()

    ch._log_start_time = MagicMock()
    ch._record_tracking_stack = [MagicMock()]
    ch._active_record_book = MagicMock()

    with ch.new_record() as record:
        assert record is not None
        record.set_name('test_record')
        record.record_metadata()
        assert ch._active_record_book.handler.add_record.called


def test_new_record_log_records_compromised(caplog):
    ch = Chronicle()

    ch._log_start_time = MagicMock()
    ch._record_tracking_stack = []
    ch._active_record_book = MagicMock()

    with pytest.raises(ValueError, match="Log records compromised."):
        with ch.new_record():
            pass
