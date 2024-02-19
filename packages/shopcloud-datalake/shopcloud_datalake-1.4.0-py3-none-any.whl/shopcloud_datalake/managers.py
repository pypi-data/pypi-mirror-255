from abc import ABC, abstractmethod


class AbstractAdapterManager(ABC):
    def __init__(self, hub, **kwargs) -> None:
        self.hub = hub
        self.datas = {}
        self.config = kwargs.get("config", {})
        self.debug = kwargs.get("debug", False)

    def register(self, name: str, adapter) -> None:
        self.datas[name] = adapter

    @abstractmethod
    def get(self, name: str, **kwargs):
        pass
