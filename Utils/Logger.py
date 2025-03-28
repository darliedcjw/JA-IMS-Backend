import logging
from logging.config import dictConfig
from contextvars import ContextVar
import yaml
import os

sessionIDVar = ContextVar("sessionID", default="NO_SESSION")


class SessionIDFilter(logging.Filter):
    def filter(self, record):
        # If session_id is not already set, use the default value
        record.session_id = sessionIDVar.get()
        return True


def createLogger():
    if not os.path.exists("Logs"):
        os.makedirs("Logs")

    if not logging.root.handlers:
        with open("Configs/Logger.yaml", "r") as file:
            config = yaml.safe_load(file)
            dictConfig(config)

    logger = logging.getLogger()

    for handler in logger.handlers:
        if not any(
            isinstance(handlerFilter, SessionIDFilter)
            for handlerFilter in handler.filters
        ):
            handler.addFilter(SessionIDFilter())

    return logger
