"""
Pytonic wrapper for the standard logging module
"""


import types
from logging import *


add_level_name = addLevelName
basic_config = basicConfig
get_logger = getLogger


StreamHandler.add_filter = StreamHandler.addFilter
StreamHandler.handle_error = StreamHandler.handleError
StreamHandler.remove_filter = StreamHandler.removeFilter
StreamHandler.set_formatter = StreamHandler.setFormatter
StreamHandler.set_formatter = StreamHandler.setFormatter
StreamHandler.set_level = StreamHandler.setLevel
StreamHandler.set_stream = StreamHandler.setStream


Logger.add_filter = Logger.addFilter
Logger.add_handler = Logger.addHandler
Logger.call_handlers = Logger.callHandlers
Logger.find_caller = Logger.findCaller
Logger.get_child = Logger.getChild
Logger.get_children = Logger.getChildren
Logger.get_effective_level = Logger.getEffectiveLevel
Logger.has_handlers = Logger.hasHandlers
Logger.is_enabled_for = Logger.isEnabledFor
Logger.make_record = Logger.makeRecord
Logger.remove_filter = Logger.removeFilter
Logger.remove_handler = Logger.removeHandler
Logger.set_level = Logger.setLevel


_RED = "\x1b[31m"
_RED_BACKGROUND = "\x1b[41m"
_GREEN = "\x1b[32m"
_YELLOW = "\x1b[33m"
_BLUE = "\x1b[34m"
_MAGENTA = "\x1b[35m"
_CYAN = "\x1b[36m"
_WHITE = "\x1b[37m"
_RESET = "\x1b[0m"


_LEVEL_COLOR_MAPPING = {
    DEBUG: _YELLOW,
    INFO: _GREEN,
    WARNING: _MAGENTA,
    ERROR: _RED,
    CRITICAL: _RED_BACKGROUND,
}


class ColoredFormatter(Formatter, ):
    def format(self, record, ):
        color = _LEVEL_COLOR_MAPPING.get(record.levelno, _RESET, )
        colored_fmt = color + self._fmt + _RESET
        formatter = Formatter(colored_fmt, )
        return formatter.format(record, )


def get_colored_logger(
    name: str | None = None,
    propagate: bool = True,
    level: int = WARNING,
    format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    remove_existing_handlers: bool = True,
) -> Logger:
    logger = get_logger(name, )
    logger.clear_handlers = types.MethodType(clear_handlers, logger, )
    logger.propagate = propagate
    if remove_existing_handlers:
        logger.clear_handlers()
    handler = StreamHandler()
    formatter = ColoredFormatter(format, )
    handler.set_formatter(formatter, )
    logger.add_handler(handler, )
    logger.set_level(level, )
    logger._decorated = True
    return logger


def clear_handlers(logger: Logger, ) -> None:
    for handler in logger.handlers:
        logger.remove_handler(handler, )


