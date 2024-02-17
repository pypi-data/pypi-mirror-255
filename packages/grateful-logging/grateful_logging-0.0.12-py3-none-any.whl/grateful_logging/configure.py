import logging
import logging.config
from typing import TYPE_CHECKING, Optional
from grateful_logging.parser.base import BaseConfigurationParser


if TYPE_CHECKING:
    from pathlib import Path


class GratefulLoggingConfigurator:
    def __init__(self, *, parser: "Optional[BaseConfigurationParser]" = None) -> None:
        if parser is None:
            from grateful_logging.parser.json_file import JSONFileParser

            parser = JSONFileParser()

        self._parser = parser

    def setup_logging(self, file_path: "Path | str"):
        config = self._parser.parse(file_path)
        return logging.config.dictConfig(config)
