from abc import ABC, abstractmethod

class BaseModelHandler(ABC):
    """
    Abstract base class for a ModelHandler.

    Deployments are required to inherit from this base class and subsequently
    implement these functions when defining their ModelHandler.
    """

    @abstractmethod
    def load(self, path: str):
        pass

    @abstractmethod
    def infer(self, model, input):
        pass

    @abstractmethod
    def decode_input(self, data):
        pass

    @abstractmethod
    def encode_output(self, data):
        pass
