import h5py
import numpy as np
import pathlib

from labchronicle.handlers import RecordHandlerHDF5


def test_record_handler_hdf5_integration(tmp_path):
    log_path = str(tmp_path / "test.hdf5")
    config = {"log_path": log_path}
    handler = RecordHandlerHDF5(config)

    handler.init_new_record_book()

    # Write data using RecordHandlerHDF5
    sample_data = {"group": {"dataset": [1, 2, 3, 4, 5]}}
    with handler._open_file('a') as file:
        for group_name, datasets in sample_data.items():
            group = file.create_group(group_name)
            for dataset_name, data in datasets.items():
                group.create_dataset(dataset_name, data=data)

    # Check data using h5py directly
    with h5py.File(log_path, 'r') as h5:
        assert "group" in h5
        assert "dataset" in h5["group"]
        assert list(h5["group"]["dataset"]) == [1, 2, 3, 4, 5]

    # Read data using RecordHandlerHDF5
    with handler._open_file('r') as file:
        assert "group" in file
        assert "dataset" in file["group"]
        assert list(file["group"]["dataset"]) == [1, 2, 3, 4, 5]


def test_add_record(tmp_path):
    log_path = str(tmp_path / "test.hdf5")
    config = {"log_path": log_path}
    handler = RecordHandlerHDF5(config)
    handler.init_new_record_book()

    record = np.random.rand(10, 10)

    handler.add_record(pathlib.Path('group/dataset'), record)
    with h5py.File(log_path, 'r') as h5:
        assert "group" in h5
        assert "dataset" in h5["group"]
        assert np.allclose(h5["group"]["dataset"], record)


def test_list_records(tmp_path):
    log_path = str(tmp_path / "test.hdf5")
    config = {"log_path": log_path}
    handler = RecordHandlerHDF5(config)
    handler.init_new_record_book()

    record = np.random.rand(10, 10)

    handler.add_record(pathlib.Path('group/dataset'), record)

    assert list(handler.list_records(pathlib.Path('/'))) == ['group','root']
    assert list(handler.list_records(pathlib.Path('/group'))) == ['dataset']
