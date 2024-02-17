import logging
import os
from typing import Callable

from sentry_sdk import push_scope

from rnd_logger.config import configure_logging
from rnd_logger.incident_severity import IncidentSeverity

class _RnDLogger(logging.RootLogger):
    def __init__(self, logger, sentry_push_scope_method: Callable) -> None:
        super().__init__(os.getenv("LOGGING_LEVEL", logging.getLevelName(logging.INFO)))
        self.__logger = logger
        self.__sentry_scope_provider = sentry_push_scope_method

    def debug(self, msg, *args, **kwargs):
        self.__logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.__logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.__logger.warning(msg, *args, **kwargs)

    def error_office_hours_alert(self, msg, runbook_url: str = None, *args, **kwargs):
        self.__log_error(msg, runbook_url, IncidentSeverity.MAJOR, *args, **kwargs)

    def error_out_of_hours_alert(self, msg, runbook_url: str = None, *args, **kwargs):
        self.__log_error(msg, runbook_url, IncidentSeverity.CRITICAL, *args, **kwargs)

    def __log_error(
            self,
            msg,
            runbook_url: str = None,
            severity: IncidentSeverity = None,
            *args,
            **kwargs
    ):
        with self.__sentry_scope_provider() as scope:
            if severity is not None:
                scope.set_tag("severity", severity.name.lower())
            if runbook_url is None:
                self.__logger.warning("Runbook url missing for error", stack_info=True)

            scope.set_tag("runbook_url", runbook_url)
            self.__logger.error(msg, *args, **kwargs)

def get_logger(name=None):
    configure_logging()
    return _RnDLogger(logging.getLogger(name), push_scope)
