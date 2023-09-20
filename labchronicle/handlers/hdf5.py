from typing import Any, Union
import h5py
from contextlib import contextmanager
import pathlib

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
    def _open_file(self, mode):
        """
            Open the HDF5 file. Use `with` statement with this function to operate hdf5 files.

            Parameters:
                mode (str): The mode to open the file.

            Returns:
                file: The HDF5 file object.
        """

        h5 = h5py.File(self._config['log_path'], mode)
        try:
            yield h5
        finally:
            h5.close()

    def init_new_record_book(self):
        """
        Initialize a new record book.
        """
        with self._open_file('w'):
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

    def get_record_by_id(self, record_id: str):
        """
        Get a record by its id.

        Parameters:
            record_id (str): The record id.

        Returns:
            Any: The record.
        """
        self._check_initiated()

        raise NotImplementedError()

    def get_record_by_timestamp(self, record_time: int):
        """
        Get a record by its timestamp.

        Parameters:
            record_time (int): The timestamp of the record.

        Returns:
            Any: The record.
        """

        # Iterate through all the records and do binary search
        self._check_initiated()

        raise NotImplementedError()

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
