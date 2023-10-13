import os
import pathlib

import pytest
import numpy as np

from labchronicle import Chronicle, LoggableObject, log_and_record, load_object, load_attributes


class MockChronicle(Chronicle):
    """
    A mock class for testing MockChronicle. Allows killing the singleton instance.
    """

    @classmethod
    def kill_singleton(cls):
        cls._instance = None


class SampleClass(LoggableObject):
    def __init__(self):
        super().__init__()
        self.config = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        self.data = np.arange(10)

    @log_and_record()
    def sample_method_1(self, a, b, c=1):
        self.data = np.arange(20)
        self.ai = a
        self.bi = b
        self.ci = c
        return 'abc'

    @log_and_record()
    def sample_method_2(self, d, e, f=1):
        self.data = np.arange(30)
        return 123


def test_create_log(tmp_path):
    os.environ['LAB_CHRONICLE_LOG_DIR'] = str(tmp_path)
    chronicle = MockChronicle(config_path=None)

    chronicle.start_log('test_log')

    assert chronicle._active_record_book is not None

    chronicle.end_log()
    assert chronicle._active_record_book is None

    chronicle.kill_singleton()


def test_run_logs_and_read_logs(tmp_path):
    os.environ['LAB_CHRONICLE_LOG_DIR'] = str(tmp_path)
    chronicle = Chronicle(config_path=None)

    chronicle.start_log('')

    sample_class = SampleClass()
    sample_class.sample_method_1(1, 2, c=3)

    assert chronicle._active_record_book is not None

    sample_class.sample_method_2(4, 5, f=6)

    path = chronicle._active_record_book.get_path()
    chronicle.end_log()

    # Test using record details to load record
    record_details = sample_class.retrieve_latest_record_entry_details(sample_class.sample_method_1)
    attributes = load_attributes(record_book_path=str(record_details['record_book_path']),
                                 record_entry_path=str(record_details['record_entry_path']))
    assert attributes['ai'] == 1

    attributes = load_attributes(record_book_path=str(record_details['record_book_path']),
                                 record_id=str(record_details['record_id']))
    assert attributes['ai'] == 1

    loaded_obj = load_object(record_book_path=str(record_details['record_book_path']),
                             record_entry_path=str(record_details['record_entry_path']))
    assert loaded_obj.ai == 1

    loaded_obj = load_object(record_book_path=str(record_details['record_book_path']),
                             record_id=str(record_details['record_id']))

    assert loaded_obj.ai == 1
    assert loaded_obj.retrieve_args(func=loaded_obj.sample_method_1) == {'a': 1, 'b': 2, 'c': 3}

    # Test using record book to load record
    record_book = chronicle.open_record_book(path)

    root_entry = record_book.get_root_entry()

    children = root_entry.children

    assert len(children) == 2

    # Check the parent of the children is correctly set
    for i, child in enumerate(children):
        assert child.record_order == i
        assert child.parent.get_path() == root_entry.get_path()

    # Check the children are correctly set for simple_method_1
    sample_method_1_entry = children[0]
    assert sample_method_1_entry.name == 'SampleClass.sample_method_1'
    assert str(sample_method_1_entry.get_path()) == '/root/0-SampleClass.sample_method_1'
    assert sample_method_1_entry.get_children_number() == 0
    assert sample_method_1_entry.get_recorded_attribute_names() == ['data', 'ai', 'bi', 'ci']
    assert sample_method_1_entry.load_attribute('ai') == 1
    assert sample_method_1_entry.load_attribute('bi') == 2
    assert sample_method_1_entry.load_attribute('ci') == 3
    assert np.allclose(sample_method_1_entry.load_attribute('data'), np.arange(20))
    assert sample_method_1_entry.load_return_values() == 'abc'

    # Check the children are correctly set for simple_method_2
    sample_method_2_entry = children[1]
    assert sample_method_2_entry.name == 'SampleClass.sample_method_2'
    assert str(sample_method_2_entry.get_path()) == '/root/1-SampleClass.sample_method_2'
    assert sample_method_2_entry.get_children_number() == 0
    assert sample_method_2_entry.get_recorded_attribute_names() == ['data']
    assert np.allclose(sample_method_2_entry.load_attribute('data'), np.arange(30))
    assert sample_method_2_entry.load_return_values() == 123
