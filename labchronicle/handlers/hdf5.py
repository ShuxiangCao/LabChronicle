import pickle
from typing import Any, Union
import h5py
from contextlib import contextmanager
import pathlib

import numpy as np

from .handlers import RecordHandlersBase


class RecordHandlerHDF5(RecordHandlersBase):
    """
    The HDF5 handler.
    """

    def __init__(self, config: dict):
        """
        Initialize the handler.
        """
        super().__init__(config)
        pass

    @contextmanager
    def _open_file(self, mode: str):
        """
            Open the HDF5 file. Use `with` statement with this function to operate hdf5 files.

            Parameters:
                mode (str): The mode to open the file.

            Returns:
                file: The HDF5 file object.
        """

        path = self._config['log_path']

        if isinstance(path, str):
            path = pathlib.Path(path)

        if not path.parent.exists():
            path.parent.mkdir(parents=True)

        h5 = h5py.File(path, mode)
        try:
            yield h5
        finally:
            h5.close()

    def init_new_record_book(self):
        """
        Initialize a new record book.
        """
        with self._open_file('w') as f:
            f.create_group('root')
            pass
        self._initiated = True

    def load_record_book(self):
        """
        Load an existing record book.
        """
        with self._open_file('r'):
            pass
        self._initiated = True

    def add_record(self, record_path: Union[pathlib.Path, str], record: Any):
        """
        Add a record to the database.

        Parameters:
            record_path (pathlib.Path): The path to the record.
            record (Any): The record to add.
        """

        self._check_initiated()

        if isinstance(record_path, pathlib.Path):
            record_path = record_path.as_posix()

        # Check the data type
        if isinstance(record, np.ndarray):
            # Save numpy directly
            pass
        elif isinstance(record, str):
            # Save string directly
            pass
        else:
            # Pickle and convert to np.void
            pickled_record = pickle.dumps(record)
            record = np.void(pickled_record)

        with self._open_file('a') as f:
            f.create_dataset(record_path, data=record)

    def get_record_by_path(self, record_path: Union[pathlib.Path, str]):
        """
        Get a record by its path.

        Parameters:
            record_path (pathlib.Path or str): The path to the record.

        Returns:
            Any: The record.
        """
        self._check_initiated()

        if isinstance(record_path, pathlib.Path):
            record_path = record_path.as_posix()

        with self._open_file('r') as f:
            return f[record_path][()]

    def list_records(self, record_path: Union[pathlib.Path, str]) -> list:
        """
        List all the records under the given path.

        Parameters:
            record_path (pathlib.Path or str): The path to the record.

        Returns:
            pathlib.Path: A list of records.
        """
        self._check_initiated()

        if isinstance(record_path, pathlib.Path):
            record_path = record_path.as_posix()

        with self._open_file('r') as f:
            return list(f[record_path].keys())