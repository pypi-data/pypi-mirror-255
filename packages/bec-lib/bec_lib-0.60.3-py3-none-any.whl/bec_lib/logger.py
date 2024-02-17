from __future__ import annotations

import enum
import json
import sys
from typing import TYPE_CHECKING

from loguru import logger as loguru_logger

# TODO: Importing bec_lib, instead of `from bec_lib.messages import LogMessage`, avoids potential
# logger <-> messages circular import. But there could be a better solution.
import bec_lib
from bec_lib.endpoints import MessageEndpoints

if TYPE_CHECKING:
    from bec_lib.connector import ConnectorBase


class LogLevel(int, enum.Enum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    CONSOLE_LOG = 21


class BECLogger:
    DEBUG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> |"
        " <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> -"
        " <level>{message}</level>"
    )
    LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>[{level}]</level> |"
        " <level>{message}</level>"
    )
    LOGLEVEL = LogLevel

    def __init__(self) -> None:
        if hasattr(self, "_configured"):
            return
        self.bootstrap_server = None
        self.connector = None
        self.service_name = None
        self.producer = None
        self.logger = loguru_logger
        self._log_level = LogLevel.INFO
        self.level = self._log_level
        self._configured = False
        self.logger.level("CONSOLE_LOG", no=21, color="<yellow>", icon="📣")

    def __new__(cls):
        if not hasattr(cls, "_logger"):
            cls._logger = super(BECLogger, cls).__new__(cls)
            cls._initialized = False
        return cls._logger

    def configure(
        self, bootstrap_server: list, connector_cls: ConnectorBase, service_name: str
    ) -> None:
        """
        Configure the logger.

        Args:
            bootstrap_server (list): List of bootstrap servers.
            connector_cls (ConnectorBase): Connector class.
            service_name (str): Name of the service to which the logger belongs.
        """

        self.bootstrap_server = bootstrap_server
        self.connector = connector_cls(bootstrap_server)
        self.service_name = service_name
        self.producer = self.connector.producer()
        self._configured = True
        self._update_sinks()

    def _logger_callback(self, msg):
        if not self._configured:
            return
        msg = json.loads(msg)
        msg["service_name"] = self.service_name
        self.producer.send(
            topic=MessageEndpoints.log(),
            msg=bec_lib.messages.LogMessage(
                log_type=msg["record"]["level"]["name"], content=msg
            ).dumps(),
        )

    def format(self, level: LogLevel = None) -> str:
        """
        Get the format for a specific log level.

        Args:
            level (LogLevel, optional): Log level. Defaults to None. If None, the current log level will be used.

        Returns:
            str: Log format.
        """
        if level is None:
            level = self.level
        if level > self.LOGLEVEL.DEBUG:
            return self.LOG_FORMAT

        return self.DEBUG_FORMAT

    def _update_sinks(self):
        self.logger.remove()
        self.add_console_log()
        self.add_redis_log(self._log_level)
        self.add_sys_stderr(self._log_level)
        self.add_file_log(self._log_level)

    def add_sys_stderr(self, level: LogLevel):
        """
        Add a sink to stderr.

        Args:
            level (LogLevel): Log level.
        """
        self.logger.add(sys.stderr, level=level, format=self.format(level), enqueue=True)

    def add_file_log(self, level: LogLevel):
        """
        Add a sink to the service log file.

        Args:
            level (LogLevel): Log level.
        """
        if not self.service_name:
            return
        self.logger.add(
            f"{self.service_name}.log", level=level, format=self.format(level), enqueue=True
        )

    def add_console_log(self):
        """
        Add a sink to the console log.
        """
        if not self.service_name:
            return
        self.logger.add(
            f"{self.service_name}_CONSOLE.log",
            level=LogLevel.CONSOLE_LOG,
            format=self.format(LogLevel.CONSOLE_LOG),
            filter=lambda record: record["level"].no == LogLevel.CONSOLE_LOG,
            enqueue=True,
        )

    def add_redis_log(self, level: LogLevel):
        """
        Add a sink to the redis log.

        Args:
            level (LogLevel): Log level.
        """
        self.logger.add(self._logger_callback, serialize=True, level=level)

    @property
    def level(self):
        """
        Get the current log level.
        """
        return self._log_level

    @level.setter
    def level(self, val: LogLevel):
        self._log_level = val
        self._update_sinks()


bec_logger = BECLogger()
