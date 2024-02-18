from abc import ABC, abstractmethod

class BaseDBConnection(ABC):
    @abstractmethod
    def execute(self, query: str, params: dict):
        """Execute the query and return status and rows count"""
        pass

    @abstractmethod
    def get_stats(self, query: str, datetime: str, params: dict):
        pass