import structlog
import logging
from structlog import DropEvent
from structlog.types import EventDict

class ConditionalDropper:
    def __call__(self, logger, method_name, event_dict):
        # print(logger.)
        if event_dict.get("event") == "request" or event_dict.get("event") == "response":
            # TODO: find proper way to ignore arsenic logs
            raise DropEvent

        return event_dict


def set_logger(level=logging.DEBUG):
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
            ConditionalDropper(),
            structlog.dev.ConsoleRenderer()
        ],
        # wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        cache_logger_on_first_use=False
    )

    # Create logger
    logg = logging.getLogger('ProxyBoostVideo')

    # We need factory, to return application-wide logger
    def logger_factory():
        return logg

    structlog.configure(logger_factory=logger_factory)
    logg.setLevel(level)
    return logg
