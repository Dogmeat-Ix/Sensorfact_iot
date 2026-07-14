from abc import ABC, abstractmethod


class BaseSensor(ABC):
    """Interface that all sensor implementations must satisfy."""

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def close(self):
        pass
