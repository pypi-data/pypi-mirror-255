from __future__ import annotations

import json
import os
import pathlib
import time
import uuid
from typing import TYPE_CHECKING

import msgpack
import yaml

import bec_lib
from bec_lib import messages
from bec_lib.bec_errors import DeviceConfigError
from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.messages import DeviceConfigMessage, RequestResponseMessage

if TYPE_CHECKING:
    from bec_lib.redis_connector import RedisConnector

logger = bec_logger.logger


class ConfigHelper:
    def __init__(self, connector: RedisConnector) -> None:
        self.connector = connector
        self.producer = connector.producer()

    def update_session_with_file(self, file_path: str, reload=True):
        """Update the current session with a yaml file from disk.

        Args:
            file_path (str): Full path to the yaml file.
            reload (bool, optional): Send a reload request to all services. Defaults to True.
        """
        config = self._load_config_from_file(file_path)
        self.send_config_request(action="set", config=config)

    def _load_config_from_file(self, file_path: str) -> dict:
        data = {}
        if pathlib.Path(file_path).suffix not in (".yaml", ".yml"):
            raise NotImplementedError

        with open(file_path, "r", encoding="utf-8") as stream:
            try:
                data = yaml.safe_load(stream)
                logger.trace(
                    f"Loaded new config from disk: {json.dumps(data, sort_keys=True, indent=4)}"
                )
            except yaml.YAMLError as err:
                logger.error(f"Error while loading config from disk: {repr(err)}")

        return data

    def save_current_session(self, file_path: str):
        """Save the current session as a yaml file to disk.

        Args:
            file_path (str): Full path to the yaml file.
        """
        msg_raw = self.producer.get(MessageEndpoints.device_config())
        config = msgpack.loads(msg_raw)
        out = {}
        for dev in config:
            dev.pop("id", None)
            dev.pop("createdAt", None)
            dev.pop("createdBy", None)
            dev.pop("sessionId", None)
            name = dev.pop("name")
            out[name] = dev

        with open(file_path, "w") as file:
            file.write(yaml.dump(out))

        print(f"Config was written to {file_path}.")

    def send_config_request(self, action: str = "update", config=None) -> None:
        """
        send request to update config
        Returns:

        """
        if action in ["update", "add", "set"] and not config:
            raise DeviceConfigError(f"Config cannot be empty for an {action} request.")
        RID = str(uuid.uuid4())
        self.producer.send(
            MessageEndpoints.device_config_request(),
            DeviceConfigMessage(action=action, config=config, metadata={"RID": RID}).dumps(),
        )

        reply = self.wait_for_config_reply(RID)

        if not reply.content["accepted"]:
            raise DeviceConfigError(f"Failed to update the config: {reply.content['message']}.")

        # wait for the device server and scan server to acknowledge the config change
        self.wait_for_service_response(RID)

    def wait_for_service_response(self, RID: str, timeout=10) -> messages.ServiceResponseMessage:
        """
        wait for service response

        Args:
            RID (str): request id
            timeout (int, optional): timeout in seconds. Defaults to 10.

        Returns:
            ServiceResponseMessage: reply message
        """
        elapsed_time = 0
        max_time = timeout
        while True:
            res = self.producer.lrange(MessageEndpoints.service_response(RID), 0, -1)
            if not res:
                time.sleep(0.005)
                elapsed_time += 0.005
            else:
                service_messages = [messages.ServiceResponseMessage.loads(msg) for msg in res]
                ack_services = [
                    msg.content["response"]["service"]
                    for msg in service_messages
                    if msg is not None
                ]
                if set(["DeviceServer", "ScanServer"]).issubset(set(ack_services)):
                    break
            if elapsed_time > max_time:
                if res:
                    service_messages = [messages.ServiceResponseMessage.loads(msg) for msg in res]
                    raise DeviceConfigError(
                        "Timeout reached whilst waiting for config change to be acknowledged."
                        f" Received {service_messages}."
                    )

                raise DeviceConfigError(
                    "Timeout reached whilst waiting for config change to be acknowledged. No"
                    " messages received."
                )

    def wait_for_config_reply(self, RID: str, timeout=10) -> RequestResponseMessage:
        """
        wait for config reply

        Args:
            RID (str): request id
            timeout (int, optional): timeout in seconds. Defaults to 10.

        Returns:
            RequestResponseMessage: reply message
        """
        start = 0
        while True:
            msg = self.producer.get(MessageEndpoints.device_config_request_response(RID))
            if msg is None:
                time.sleep(0.01)
                start += 0.01

                if start > timeout:
                    raise DeviceConfigError("Timeout reached whilst waiting for config reply.")
                continue
            return RequestResponseMessage.loads(msg)

    def load_demo_config(self):
        """Load BEC device demo_config.yaml for simulation."""
        dir_path = os.path.abspath(os.path.join(os.path.dirname(bec_lib.__file__), "./configs/"))
        fpath = os.path.join(dir_path, "demo_config.yaml")
        self.update_session_with_file(fpath)
