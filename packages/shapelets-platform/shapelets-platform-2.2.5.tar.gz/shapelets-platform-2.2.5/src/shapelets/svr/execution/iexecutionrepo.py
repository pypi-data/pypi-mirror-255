from abc import ABC, abstractmethod
from typing import List


class IExecutionRepo(ABC):

    @abstractmethod
    def add_files(self, current_fn_id: str, new_ids: List[str]):
        pass
