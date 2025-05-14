from abc import ABC, abstractmethod

class HttpException(Exception, ABC):
    @property
    @abstractmethod
    def status_code(self) -> int:
        pass

    @property
    @abstractmethod
    def message(self) -> str:
        pass