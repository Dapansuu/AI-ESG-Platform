from abc import ABC, abstractmethod


class BaseNode(ABC):

    @abstractmethod
    def run(self, state):
        pass

    def execute(self, state):
        return self.run(state)