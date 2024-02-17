import atexit
import logging
from queue import Queue
from typing import TYPE_CHECKING, Sequence
from logging.handlers import QueueHandler as _QueueHandler, QueueListener


if TYPE_CHECKING:
    from typing import Any, Optional
    from logging.handlers import _QueueLike


class QueueHandler(_QueueHandler):
    def __init__(
        self,
        handlers: Sequence[logging.Handler],
        queue: "Optional[_QueueLike[Any]]" = None,
        listener: "Optional[QueueListener]" = None,
        respect_handler_level: bool = False,
        auto_start_thread: bool = True,
        auto_register_shutdown: bool = True,
        **kwargs,
    ) -> None:
        _handlers = []
        handlers_map = dict(getattr(logging, "_handlers"))

        for handler_name in handlers:
            if not (handler := handlers_map.get(handler_name)):
                raise ValueError(f'Handler "{handler_name}" not found')

            _handlers.append(handler)

        queue = queue if queue is not None else Queue()
        super().__init__(queue, **kwargs)
        self.listener = listener or QueueListener(
            self.queue,
            *_handlers,
            respect_handler_level=respect_handler_level,
        )

        if auto_start_thread:
            self.listener.start()

        if auto_register_shutdown:
            atexit.register(self._shutup)

        handlers_map = dict(getattr(logging, "_handlers"))

    def _shutup(self):
        self.listener.stop()
