import h5py
import numpy as np
import pathlib

from labchronicle.handlers import RecordHandlerMemory  # Update the import path as necessary


def test_record_handler_memory_integration():
    config = {"max_records": 5}
    handler = RecordHandlerMemory(config)

    handler.init_new_record_book()

    # Write data using RecordHandlerMemory
    sample_data = [("group/dataset", [1, 2, 3, 4, 5])]
    for record_path, data in sample_data:
        handler.add_record(record_path, data)

    # Read data using RecordHandlerMemory
    retrieved_data = handler.get_record_by_path("group/dataset")
    assert retrieved_data == [1, 2, 3, 4, 5]

    # Test automatic removal of old records
    for i in range(6):
        handler.add_record(f"new/data{i}", [i])

    # Old record ("group/dataset") should be removed, and only the last 5 records remain
    assert handler.get_record_by_path("group/dataset") is None
    assert handler.get_record_by_path("new/data1") == [1]


def test_add_record():
    config = {"max_records": 5}
    handler = RecordHandlerMemory(config)
    handler.init_new_record_book()

    record = np.random.rand(10, 10)

    handler.add_record('group/dataset', record)
    retrieved_record = handler.get_record_by_path('group/dataset')
    assert np.allclose(retrieved_record, record)


def test_list_records():
    config = {"max_records": 5}
    handler = RecordHandlerMemory(config)
    handler.init_new_record_book()

    record = np.random.rand(10, 10)
    handler.add_record('group/dataset', record)

    # Test listing records
    expected_records = ['group/dataset']
    records_list = handler.list_records()
    assert set(records_list) == set(expected_records)
