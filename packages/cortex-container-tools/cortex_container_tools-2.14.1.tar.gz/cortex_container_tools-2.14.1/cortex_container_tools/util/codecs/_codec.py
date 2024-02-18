from abc import ABC, abstractmethod

class Codec(ABC):
    @staticmethod
    @abstractmethod
    def decode(data):
        pass

    @staticmethod
    @abstractmethod
    def encode(data):
        pass
