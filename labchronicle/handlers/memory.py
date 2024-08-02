import pickle
from typing import Any, Union
from collections import deque
import numbers

import numpy as np

from .handlers import RecordHandlersBase


class RecordHandlerMemory(RecordHandlersBase):
    """
    An in-memory record handler.
    """

    def __init__(self, config: dict):
        """
        Initialize the handler.
        """
        super().__init__(config)
        self.records = deque(maxlen=config.get('max_records', 5))  # Use deque to auto-remove oldest entries
        self._initiated = True

    def init_new_record_book(self):
        """
        Initialize a new record book.
        """
        self.records.clear()
        self._initiated = True

    def load_record_book(self):
        """
        Load an existing record book.
        """
        # No action needed for memory-based loading.
        self._initiated = True

    def add_record(self, record_path: Union[str, Any], record: Any):
        """
        Add a record to the memory.

        Parameters:
            record_path (str): A unique identifier for the record.
            record (Any): The record to add.
        """
        self._check_initiated()

        # Serialize non-primitive data types
        if isinstance(record, (np.ndarray, dict, list)):
            record = pickle.dumps(record)

        # Store the record using record_path as the key
        self.records.append((record_path, record))

    def get_record_by_path(self, record_path: str):
        """
        Get a record by its path.

        Parameters:
            record_path (str): The path to the record.

        Returns:
            Any: The record if found, otherwise None.
        """
        self._check_initiated()
        for path, record in self.records:
            if path == record_path:
                if isinstance(record, bytes):
                    return pickle.loads(record)  # Unpickle if the record is serialized
                return record
        return None  # Return None if not found

    def list_records(self) -> list:
        """
        List all records' paths.

        Returns:
            list: A list of record paths.
        """
        self._check_initiated()
        return [path for path, _ in self.records]
