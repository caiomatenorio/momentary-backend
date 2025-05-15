from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class HttpException(Exception, ABC):
    @property
    @abstractmethod
    def status_code(self) -> int:
        pass

    @property
    @abstractmethod
    def message(self) -> str:
        pass
