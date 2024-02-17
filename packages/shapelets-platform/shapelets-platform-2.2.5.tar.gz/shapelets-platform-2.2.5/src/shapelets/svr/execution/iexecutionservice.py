from abc import ABC, abstractmethod
from typing import Any

from ..model.function import FunctionProfile


class IExecutionService(ABC):
    @abstractmethod
    def execute_function(self, fn: FunctionProfile) -> Any:
        """
        Invoke the serialization function and return its output. This method is called by the UI to retrieve the
        generated widget resulting from a bound execution.
        """
        pass

    @abstractmethod
    def table_data(self, table: str, from_row: int, to_row: int) -> str:
        """
        Retrieve the specified data from a table. This method is invoked by the UI to obtain the next page of the table.
        """
        pass

    @abstractmethod
    def save_table(self, table_id: str, data: str):
        """
        Given a serialized Arrow Table and an identifier (ID), store the table in a file using the ID as the filename.
        """
        pass
