import json
import os

import yaml

from bec_lib.logger import bec_logger

try:
    from bec_plugins.utils import load_service_config as plugin_load_service_config
except ImportError:
    plugin_load_service_config = None

logger = bec_logger.logger

DEFAULT_SERVICE_CONFIG = {
    "redis": {"host": "localhost", "port": 6379},
    "service_config": {"file_writer": {"plugin": "default_NeXus_format", "base_path": "./"}},
}


class ServiceConfig:
    def __init__(
        self, config_path: str = None, redis: dict = None, config: dict = None, **kwargs
    ) -> None:
        self.config_path = config_path
        self.config = {}
        self._load_config()
        if self.config:
            self._load_urls("redis", required=True)
            self._load_urls("mongodb", required=False)

        self._update_config(service_config=config, redis=redis)

        self.service_config = self.config.get(
            "service_config", {"file_writer": {"plugin": "default_NeXus_format", "base_path": "./"}}
        )

    def _update_config(self, **kwargs):
        for key, val in kwargs.items():
            if not val:
                continue
            self.config[key] = val

    def _load_config(self):
        if self.config_path:
            with open(self.config_path, "r") as stream:
                self.config = yaml.safe_load(stream)
                logger.info(
                    "Loaded new config from disk:"
                    f" {json.dumps(self.config, sort_keys=True, indent=4)}"
                )
            return
        if os.environ.get("BEC_SERVICE_CONFIG"):
            self.config = json.loads(os.environ.get("BEC_SERVICE_CONFIG"))
            logger.info(
                "Loaded new config from environment:"
                f" {json.dumps(self.config, sort_keys=True, indent=4)}"
            )
            return
        if plugin_load_service_config:
            self.config = plugin_load_service_config()
            logger.info(
                "Loaded new config from plugin:"
                f" {json.dumps(self.config, sort_keys=True, indent=4)}"
            )
            return
        if not self.config_path:
            self.config = DEFAULT_SERVICE_CONFIG
            return

    def _load_urls(self, entry: str, required: bool = True):
        config = self.config.get(entry)
        if config:
            return f"{config['host']}:{config['port']}"

        if required:
            raise ValueError(
                f"The provided config does not specify the url (host and port) for {entry}."
            )
        return ""

    @property
    def redis(self):
        return self._load_urls("redis", required=True)

    @property
    def abort_on_ctrl_c(self):
        return self.service_config.get("abort_on_ctrl_c", True)
