from abc import ABC, abstractmethod


class BaseConfigurationParser(ABC):
    @abstractmethod
    def parse(self, file_path) -> dict:
        pass
