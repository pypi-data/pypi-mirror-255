from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

from typeguard import typechecked

from bec_lib import messages
from bec_lib.device import DeviceBase
from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.scan_items import ScanItem
from bec_lib.signature_serializer import dict_to_signature

logger = bec_logger.logger

if TYPE_CHECKING:
    from bec_lib.client import BECClient


class DAPPluginObject:
    def __init__(
        self,
        service_name: str,
        plugin_info: dict,
        client: BECClient = None,
        auto_run_supported: bool = False,
        service_info: dict = None,
    ) -> None:
        self._service_name = service_name
        self._plugin_info = plugin_info
        self._client = client
        self._auto_run_supported = auto_run_supported
        self._plugin_config = {}
        self._service_info = service_info

        # run must be an anonymous function to allow for multiple doc strings
        self._user_run = lambda *args, **kwargs: self._run(*args, **kwargs)

    def _run(self, *args, **kwargs):
        converted_args = []
        for arg in args:
            if isinstance(arg, ScanItem):
                converted_args.append(arg.scanID)
            else:
                converted_args.append(arg)
        args = converted_args
        converted_kwargs = {}
        for key, val in kwargs.items():
            if isinstance(val, ScanItem):
                converted_kwargs[key] = val.scanID
            else:
                converted_kwargs[key] = val
        kwargs = converted_kwargs
        request_id = str(uuid.uuid4())
        self._client.producer.set_and_publish(
            MessageEndpoints.dap_request(),
            messages.DAPRequestMessage(
                dap_cls=self._plugin_info["class"],
                dap_type="on_demand",
                config={
                    "args": args,
                    "kwargs": kwargs,
                    "class_args": self._plugin_info.get("class_args"),
                    "class_kwargs": self._plugin_info.get("class_kwargs"),
                },
                metadata={"RID": request_id},
            ),
        )

        response = self._wait_for_dap_response(request_id)
        return response.content["data"]

    def _wait_for_dap_response(self, request_id: str, timeout: float = 5.0):
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for DAP response.")
            response = self._client.producer.get(MessageEndpoints.dap_response(request_id))
            if not response:
                time.sleep(0.005)
                continue

            if response.metadata["RID"] != request_id:
                time.sleep(0.005)
                continue

            if response.content["success"]:
                return response
            raise RuntimeError(response.content["error"])

    @property
    def auto_run(self):
        """
        Set to True to start a continously running worker.
        """
        return self._plugin_config.get("auto_run", False)

    @auto_run.setter
    @typechecked
    def auto_run(self, val: bool):
        self._plugin_config["auto_run"] = val
        request_id = str(uuid.uuid4())
        self._update_dap_config(request_id=request_id)

    def select(self, device: DeviceBase | str, signal: str = None):
        """
        Select the device and signal to use for fitting.

        Args:
            device (DeviceBase | str): The device to use for fitting. Can be either a DeviceBase object or the name of the device.
            signal (str, optional): The signal to use for fitting. If not provided, the first signal in the device's hints will be used.
        """
        bec_device = (
            device
            if isinstance(device, DeviceBase)
            else self._client.device_manager.devices.get(device)
        )
        if not bec_device:
            raise AttributeError(f"Device {device} not found.")
        if signal:
            self._plugin_config["selected_device"] = [bec_device.name, signal]
        else:
            # pylint: disable=protected-access
            hints = bec_device._hints
            if not hints:
                raise AttributeError(
                    f"Device {bec_device.name} has no hints. Cannot select device without signal."
                )
            if len(hints) > 1:
                raise AttributeError(
                    f"Device {bec_device.name} has multiple hints. Please specify a signal."
                )
            self._plugin_config["selected_device"] = [bec_device.name, hints[0]]

        request_id = str(uuid.uuid4())
        self._update_dap_config(request_id=request_id)

    def get_data(self):
        """
        Get the data from last run.
        """
        msg = self._client.producer.get_last(MessageEndpoints.processed_data(self._service_name))
        if not msg:
            return None
        return msg.content["data"]

    def _update_dap_config(self, request_id: str = None):
        if not self._plugin_config.get("selected_device"):
            return
        self._plugin_config["class_args"] = self._plugin_info.get("class_args")
        self._plugin_config["class_kwargs"] = self._plugin_info.get("class_kwargs")
        self._client.producer.set_and_publish(
            MessageEndpoints.dap_request(),
            messages.DAPRequestMessage(
                dap_cls=self._plugin_info["class"],
                dap_type="continuous",
                config=self._plugin_config,
                metadata={"RID": request_id},
            ),
        )


class DAPPlugins:
    """
    DAPPlugins is a class that provides access to all available DAP plugins.
    """

    def __init__(self, parent):
        self._parent = parent
        self._available_dap_plugins = {}
        self._import_dap_plugins()
        self._selected_model = None
        self._auto_run = False
        self._selected_device = None

    def refresh(self):
        """
        Refresh the list of available DAP plugins. This is useful if new plugins have been added after
        the client has been initialized. This method is called automatically when the client is initialized.
        A call to this method is indempotent, meaning it can be called multiple times without side effects.
        """
        self._import_dap_plugins()

    def _import_dap_plugins(self):
        available_services = self._parent.service_status
        if not available_services:
            # not sure how we got here...
            return
        dap_services = [
            service for service in available_services if service.startswith("DAPServer/")
        ]
        for service in dap_services:
            available_plugins = self._parent.producer.get(
                MessageEndpoints.dap_available_plugins(service)
            )
            if available_plugins is None:
                logger.warning("No plugins available. Are redis and the BEC server running?")
                return
            for plugin_name, plugin_info in available_plugins.content["resource"].items():
                try:
                    if plugin_name in self._available_dap_plugins:
                        continue
                    name = plugin_info["user_friendly_name"]
                    auto_run_supported = plugin_info.get("auto_run_supported", False)
                    self._available_dap_plugins[name] = DAPPluginObject(
                        name,
                        plugin_info,
                        client=self._parent,
                        auto_run_supported=auto_run_supported,
                        service_info=available_services[service].content,
                    )
                    self._set_plugin(
                        name,
                        plugin_info.get("class_doc"),
                        plugin_info.get("run_doc"),
                        plugin_info.get("run_name"),
                        plugin_info.get("signature"),
                    )
                # pylint: disable=broad-except
                except Exception as e:
                    logger.error(f"Error importing plugin {plugin_name}: {e}")

    def _set_plugin(
        self,
        plugin_name: str,
        class_doc_string: str,
        run_doc_string: str,
        run_name: str,
        signature: dict,
    ):
        # pylint disable=protected-access
        setattr(self, plugin_name, self._available_dap_plugins[plugin_name])
        setattr(getattr(self, plugin_name), "__doc__", class_doc_string)
        setattr(getattr(self, plugin_name), run_name, getattr(self, plugin_name)._user_run)
        setattr(getattr(self, plugin_name)._user_run, "__doc__", run_doc_string)
        setattr(getattr(self, plugin_name)._user_run, "__signature__", dict_to_signature(signature))
