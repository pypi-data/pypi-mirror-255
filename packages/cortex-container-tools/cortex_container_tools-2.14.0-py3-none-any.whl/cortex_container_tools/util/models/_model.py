from abc import ABC, abstractmethod

class LoadableModel(ABC):
    def __init__(self):
        self._instance         = None
        self._training_steps   = []
        self._deployment_steps = []

    @property
    def instance(self):
        return self._instance

    @abstractmethod
    def from_file(path: str):
        pass
