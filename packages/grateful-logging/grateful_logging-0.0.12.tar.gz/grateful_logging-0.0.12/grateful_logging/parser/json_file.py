import json
from .base import BaseConfigurationParser


class JSONFileParser(BaseConfigurationParser):
    def parse(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.loads(file.read())
