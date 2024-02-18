from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class IRequest(ABC):
    pass


class IBasicProtocol(ABC):
    def __init__(self):
        self._name = self.__class__.__name__
        self._client = None

    @property
    def client(self):
        return self._client

    @abstractmethod
    def request(self, request: dict) -> Any:
        """ Execute a protocol related request"""
        raise NotImplementedError
    