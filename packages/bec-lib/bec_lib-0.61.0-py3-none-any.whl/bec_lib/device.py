import enum
import functools
import time
import uuid
from collections import namedtuple
from typing import Any

from typeguard import typechecked

from bec_lib import messages
from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.redis_connector import RedisProducer

logger = bec_logger.logger


class RPCError(Exception):
    """Exception raised when an RPC call fails."""


class ScanRequestError(Exception):
    """Exception raised when a scan request is rejected."""


def rpc(fcn):
    """Decorator to perform rpc calls."""

    @functools.wraps(fcn)
    def wrapper(self, *args, **kwargs):
        # pylint: disable=protected-access
        return self._run(*args, fcn=fcn, **kwargs)

    return wrapper


class DeviceStatus(enum.Enum):
    """Device status"""

    IDLE = 0
    RUNNING = 1
    BUSY = 2


class OnFailure(str, enum.Enum):
    """On failure behaviour for devices"""

    RAISE = "raise"
    BUFFER = "buffer"
    RETRY = "retry"


class ReadoutPriority(str, enum.Enum):
    """Readout priority for devices"""

    ON_REQUEST = "on_request"
    BASELINE = "baseline"
    MONITORED = "monitored"
    ASYNC = "async"
    CONTINUOUS = "continuous"


class Status:
    def __init__(self, producer: RedisProducer, RID: str) -> None:
        """
        Status object for RPC calls

        Args:
            producer (RedisProducer): Redis producer
            RID (str): Request ID
        """
        self._producer = producer
        self._RID = RID

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Status):
            return self._RID == __value._RID
        return False

    def wait(self, timeout=None):
        """wait until the request is completed"""
        sleep_time_step = 0.1
        sleep_count = 0

        def _sleep(sleep_time):
            nonlocal sleep_count
            nonlocal timeout
            time.sleep(sleep_time)
            sleep_count += sleep_time
            if timeout is not None and sleep_count > timeout:
                raise TimeoutError()

        while True:
            request_status = self._producer.lrange(
                MessageEndpoints.device_req_status(self._RID), 0, -1
            )
            if request_status:
                break
            _sleep(sleep_time_step)


class DeviceBase:
    """
    The DeviceBase class is the base class for all devices that are controlled via
    the DeviceManager. It provides a simple interface to perform RPC calls on the
    device. The DeviceBase class is not meant to be used directly, but rather to be subclassed.
    """

    def __init__(
        self,
        *,
        name: str,
        info: dict = None,
        config: dict = None,
        parent=None,
        signal_info: dict = None,
    ) -> None:
        """
        Args:
            name (dict): The name of the device.
            info (dict, optional): The device info dictionary. Defaults to None.
            parent ([type], optional): The parent object. Defaults to None.
            signal_info (dict, optional): The signal info dictionary. Defaults to None.
        """
        self.name = name
        self._signal_info = signal_info
        self._config = config
        if info is None:
            info = {}
        self._info = info.get("device_info", {})
        self.parent = parent
        self._custom_rpc_methods = {}
        self._property_container = set()
        if self._info:
            self._parse_info()

        # the following lambda is needed to support customized RPC methods with
        # doc strings and function signatures.
        # pylint: disable=unnecessary-lambda
        self.run = lambda *args, **kwargs: self._run(*args, **kwargs)

    def _run(self, *args, fcn=None, cached=False, **kwargs):
        device, func_call = self._get_rpc_func_name(fcn=fcn)

        if cached:
            return fcn(self, *args, **kwargs)
        return self._run_rpc_call(device, func_call, *args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        if name in self._property_container:
            return object.__getattribute__(self, "_run")(fcn=name, cached=False)
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:
        try:
            container = object.__getattribute__(self, "_property_container")
        except AttributeError:
            return super().__setattr__(name, value)

        if name in container:
            return object.__getattribute__(self, "_run")(
                value, fcn=name, cached=False, _set_property=True
            )

        super().__setattr__(name, value)

    @property
    def _hints(self):
        hints = self._info.get("hints")
        if not hints:
            return []
        return hints.get("fields", [])

    def get_device_config(self):
        """get the device config for this device"""
        return self._config["deviceConfig"]

    @property
    def enabled(self):
        """Returns True if the device is enabled, otherwise False."""
        # pylint: disable=protected-access
        return self.root._config["enabled"]

    @enabled.setter
    def enabled(self, val):
        # pylint: disable=protected-access
        self.update_config({"enabled": val})
        self.root._config["enabled"] = val

    @property
    def root(self):
        """Returns the root object of the device tree."""
        # pylint: disable=import-outside-toplevel
        from bec_lib.devicemanager import DeviceManagerBase

        parent = self
        while not isinstance(parent.parent, DeviceManagerBase):
            parent = parent.parent
        return parent

    @property
    def full_name(self):
        """Returns the full name of the device."""
        return self._compile_function_path().replace(".", "_")

    def _prepare_rpc_msg(
        self, rpc_id: str, request_id: str, device: str, func_call: str, *args, **kwargs
    ) -> messages.ScanQueueMessage:
        """
        Prepares an RPC message.

        Args:
            rpc_id (str): The RPC ID.
            request_id (str): The request ID.
            device (str): The device name.
            func_call (str): The function call.
            *args: The function arguments.
            **kwargs: The function keyword arguments.

        Returns:
            messages.ScanQueueMessage: The RPC message.
        """

        params = {
            "device": device,
            "rpc_id": rpc_id,
            "func": func_call,
            "args": args,
            "kwargs": kwargs,
        }
        msg = messages.ScanQueueMessage(
            scan_type="device_rpc",
            parameter=params,
            queue="primary",
            metadata={"RID": request_id, "response": True},
        )
        return msg

    def _handle_rpc_response(self, msg: messages.DeviceRPCMessage) -> Any:
        if not msg.content["success"]:
            error = msg.content["out"]
            if not isinstance(error, dict):
                error = {"error": "Exception", "msg": error, "traceback": ""}
            raise RPCError(
                f"During an RPC, the following error occured:\n{error['error']}:"
                f" {error['msg']}.\nTraceback: {error['traceback']}\n The scan will be aborted."
            )
        if msg.content.get("out"):
            print(msg.content.get("out"))
        return_val = msg.content.get("return_val")
        if not isinstance(return_val, dict):
            return return_val
        if return_val.get("type") == "status" and return_val.get("RID"):
            return Status(self.root.parent.producer, return_val.get("RID"))
        return return_val

    def _get_rpc_response(self, request_id, rpc_id) -> Any:
        queue = self.root.parent.parent.queue
        while queue.request_storage.find_request_by_ID(request_id) is None:
            time.sleep(0.01)
        scan_queue_request = queue.request_storage.find_request_by_ID(request_id)
        while scan_queue_request.decision_pending:
            time.sleep(0.01)
        if not all(scan_queue_request.accepted):
            raise ScanRequestError(
                "Function call was rejected by the server:"
                f" {scan_queue_request.response.content['message']}"
            )
        while True:
            msg = self.root.parent.producer.get(MessageEndpoints.device_rpc(rpc_id))
            if msg:
                break
            time.sleep(0.01)
        msg = messages.DeviceRPCMessage.loads(msg)

        return self._handle_rpc_response(msg)

    def _run_rpc_call(self, device, func_call, *args, wait_for_rpc_response=True, **kwargs) -> Any:
        """
        Runs an RPC call on the device. This method is used internally by the RPC decorator.
        If a call is interrupted by the user, the a stop signal is sent to this device.

        Args:
            device (str): The device name.
            func_call (str): The function call.
            *args: The function arguments.
            wait_for_rpc_response (bool, optional): If True, the method waits for the RPC response. Defaults to True.
            **kwargs: The function keyword arguments.

        Returns:
            Any: The return value of the RPC call.
        """
        try:
            # prepare RPC message
            rpc_id = str(uuid.uuid4())
            request_id = str(uuid.uuid4())
            msg = self._prepare_rpc_msg(rpc_id, request_id, device, func_call, *args, **kwargs)

            # send RPC message
            self.root.parent.producer.send(MessageEndpoints.scan_queue_request(), msg.dumps())

            # wait for RPC response
            if not wait_for_rpc_response:
                return None
            return_val = self._get_rpc_response(request_id, rpc_id)
        except KeyboardInterrupt as exc:
            self.root.stop(wait_for_rpc_response=False)
            raise RPCError("User interruption during RPC call.") from exc

        return return_val

    def _get_rpc_func_name(self, fcn=None, use_parent=False):
        func_call = [self._compile_function_path(use_parent=use_parent)]

        if fcn:
            if isinstance(fcn, str):
                func_call.append(fcn)
            else:
                func_call.append(fcn.__name__)

        full_func_call = ".".join(func_call)
        device = full_func_call.split(".", maxsplit=1)[0]
        func_call = ".".join(full_func_call.split(".")[1:])
        return (device, func_call)

    def _compile_function_path(self, use_parent=False) -> str:
        # pylint: disable=import-outside-toplevel
        from bec_lib.devicemanager import DeviceManagerBase

        if use_parent:
            parent = self.parent
        else:
            parent = self
        func_call = []
        while not isinstance(parent, DeviceManagerBase):
            func_call.append(parent.name)
            parent = parent.parent
        return ".".join(func_call[::-1])

    def _parse_info(self):
        if self._info.get("signals"):
            for signal_info in self._info.get("signals"):
                signal_name = signal_info.get("component_name")
                setattr(
                    self,
                    signal_name,
                    Signal(name=signal_name, signal_info=signal_info, parent=self),
                )
                precision = (
                    self._info.get("describe", {})
                    .get(f"{self.name}_{signal_name}", {})
                    .get("precision")
                )
                if precision is not None:
                    getattr(self, signal_name).precision = precision
        precision = self._info.get("describe", {}).get(self.name, {}).get("precision")
        if precision is not None:
            self.precision = precision
        if self._info.get("sub_devices"):
            for dev in self._info.get("sub_devices"):
                base_class = dev["device_info"].get("device_base_class")
                attr_name = dev["device_info"].get("device_attr_name")
                if base_class == "positioner":
                    setattr(self, attr_name, Positioner(name=attr_name, info=dev, parent=self))
                elif base_class == "device":
                    setattr(self, attr_name, Device(name=attr_name, info=dev, parent=self))

        for user_access_name, descr in self._info.get("custom_user_access", {}).items():
            if "type" in descr:
                if descr["type"] == "func":
                    self._custom_rpc_methods[user_access_name] = DeviceBase(
                        name=user_access_name, info=descr, parent=self
                    )
                    setattr(self, user_access_name, self._custom_rpc_methods[user_access_name].run)
                    setattr(getattr(self, user_access_name), "__doc__", descr.get("doc"))
                else:
                    self._property_container.add(user_access_name)
            else:
                self._custom_rpc_methods[user_access_name] = DeviceBase(
                    name=user_access_name,
                    info={"device_info": {"custom_user_access": descr}},
                    parent=self,
                )
                setattr(self, user_access_name, self._custom_rpc_methods[user_access_name])

    def update_config(self, update: dict) -> None:
        """
        Updates the device configuration.

        Args:
            update (dict): The update dictionary.

        """
        self.root.parent.config_helper.send_config_request(
            action="update", config={self.name: update}
        )

    @typechecked
    def set_device_config(self, val: dict):
        """set the device config for this device"""
        self._config["deviceConfig"].update(val)
        return self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"deviceConfig": self._config["deviceConfig"]}}
        )

    def get_device_tags(self) -> list:
        """get the device tags for this device"""
        return self._config.get("deviceTags", [])

    @typechecked
    def set_device_tags(self, val: list):
        """set the device tags for this device"""
        self._config["deviceTags"] = val
        return self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"deviceTags": self._config["deviceTags"]}}
        )

    @typechecked
    def add_device_tag(self, val: str):
        """add a device tag for this device"""
        if val in self._config["deviceTags"]:
            return None
        self._config["deviceTags"].append(val)
        return self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"deviceTags": self._config["deviceTags"]}}
        )

    def remove_device_tag(self, val: str):
        """remove a device tag for this device"""
        if val not in self._config["deviceTags"]:
            return None
        self._config["deviceTags"].remove(val)
        return self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"deviceTags": self._config["deviceTags"]}}
        )

    @property
    def wm(self) -> None:
        """get the current position of a device"""
        self.parent.devices.wm(self.name)

    @property
    def readout_priority(self) -> ReadoutPriority:
        """get the readout priority for this device"""
        return ReadoutPriority(self._config["readoutPriority"])

    @readout_priority.setter
    def readout_priority(self, val: ReadoutPriority):
        """set the readout priority for this device"""
        if not isinstance(val, ReadoutPriority):
            val = ReadoutPriority(val)
        self._config["readoutPriority"] = val
        return self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"readoutPriority": val}}
        )

    @property
    def on_failure(self) -> OnFailure:
        """get the failure behaviour for this device"""
        return OnFailure(self._config["onFailure"])

    @on_failure.setter
    def on_failure(self, val: OnFailure):
        """set the failure behaviour for this device"""
        if not isinstance(val, OnFailure):
            val = OnFailure(val)
        self._config["onFailure"] = val
        return self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"onFailure": self._config["onFailure"]}}
        )

    @property
    def read_only(self):
        """Whether or not the device can be set"""
        return self._config.get("readOnly", False)

    @read_only.setter
    def read_only(self, value: bool):
        """Whether or not the device is read only"""
        self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"readOnly": value}}
        )
        self._config["readOnly"] = value

    @property
    def software_trigger(self):
        """Whether or not the device can be software triggered"""
        return self._config.get("softwareTrigger", False)

    @software_trigger.setter
    def software_trigger(self, value: bool):
        """Whether or not the device can be software triggered"""
        self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"softwareTrigger": value}}
        )
        self._config["softwareTrigger"] = value

    # def read(self, cached, filter_readback=True):
    #     """get the last reading from a device"""
    #     val = self.parent.producer.get(MessageEndpoints.device_read(self.name))
    #     if not val:
    #         return None
    #     if filter_readback:
    #         return messages.DeviceMessage.loads(val).content["signals"].get(self.name)
    #     return messages.DeviceMessage.loads(val).content["signals"]
    #
    # def readback(self, filter_readback=True):
    #     """get the last readback value from a device"""
    #     val = self.parent.producer.get(MessageEndpoints.device_readback(self.name))
    #     if not val:
    #         return None
    #     if filter_readback:
    #         return DeviceMessage.loads(val).content["signals"].get(self.name)
    #     return DeviceMessage.loads(val).content["signals"]

    # @property
    # def device_status(self):
    #     """get the current status of the device"""
    #     val = self.parent.producer.get(MessageEndpoints.device_status(self.name))
    #     if val is None:
    #         return val
    #     val = DeviceStatusMessage.loads(val)
    #     return val.content.get("status")

    # @property
    # def signals(self):
    #     """get the last signals from a device"""
    #     val = self.parent.producer.get(MessageEndpoints.device_read(self.name))
    #     if val is None:
    #         return None
    #     self._signals = DeviceMessage.loads(val).content["signals"]
    #     return self._signals

    @property
    def user_parameter(self) -> dict:
        """get the user parameter for this device"""
        return self._config.get("userParameter")

    @typechecked
    def set_user_parameter(self, val: dict):
        """set the user parameter for this device"""
        self.parent.config_helper.send_config_request(
            action="update", config={self.name: {"userParameter": val}}
        )

    @typechecked
    def update_user_parameter(self, val: dict):
        """update the user parameter for this device
        Args:
            val (dict): New user parameter
        """
        param = self.user_parameter
        if param is None:
            param = {}
        param.update(val)
        self.set_user_parameter(param)

    def __eq__(self, other):
        if isinstance(other, DeviceBase):
            return other.name == self.name
        return False

    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        return f"{type(self).__name__}(name={self.name}, enabled={self.enabled})"


class OphydInterfaceBase(DeviceBase):
    @rpc
    def trigger(self, rpc_id: str):
        """
        Triggers the device.
        """

    def read(self, cached=True, use_readback=True, filter_to_hints=False):
        """
        Reads the device.

        Args:
            cached (bool, optional): If True, the cached value is returned. Defaults to True.
            use_readback (bool, optional): If True, the readback value is returned, otherwise the read value. Defaults to True.
            filter_to_hints (bool, optional): If True, the readback value is filtered to the hinted values. Defaults to False.

        Returns:
            dict: The device signals.
        """
        _, is_config_signal, cached = self._get_rpc_signal_info(cached)

        if not cached:
            signals = self._run(cached=cached, fcn=self.read)
        else:
            if is_config_signal:
                return self.read_configuration(cached=cached)
            if use_readback:
                val = self.root.parent.producer.get(
                    MessageEndpoints.device_readback(self.root.name)
                )
            else:
                val = self.root.parent.producer.get(MessageEndpoints.device_read(self.root.name))

            if not val:
                return None
            signals = messages.DeviceMessage.loads(val).content["signals"]
        if filter_to_hints:
            signals = {key: val for key, val in signals.items() if key in self._hints}
        return self._filter_rpc_signals(signals)

    def read_configuration(self, cached=True):
        """
        Reads the device configuration.

        Args:
            cached (bool, optional): If True, the cached value is returned. Defaults to True.
        """

        is_signal, is_config_signal, cached = self._get_rpc_signal_info(cached)

        if not cached:
            fcn = self.read_configuration if (not is_signal or is_config_signal) else self.read
            signals = self._run(cached=False, fcn=fcn)
        else:
            if is_signal and not is_config_signal:
                return self.read(cached=True)

            val = self.root.parent.producer.get(
                MessageEndpoints.device_read_configuration(self.root.name)
            )
            if not val:
                return None
            signals = messages.DeviceMessage.loads(val).content["signals"]

        return self._filter_rpc_signals(signals)

    def _filter_rpc_signals(self, signals):
        if self._signal_info:
            obj_name = self._signal_info.get("obj_name")
            return {obj_name: signals.get(obj_name, {})}
        return {key: val for key, val in signals.items() if key.startswith(self.full_name)}

    def _get_rpc_signal_info(self, cached: bool):
        is_config_signal = False
        is_signal = self._signal_info is not None
        if is_signal:
            kind = self._signal_info.get("kind_str")
            if kind == "Kind.config":
                is_config_signal = True
            elif kind == "Kind.omitted":
                cached = False
        return is_signal, is_config_signal, cached

    @rpc
    def describe(self):
        """
        Describes the device and yields information about the device's signals, including
        the signal's name, source, shape, data type, precision etc.
        """

    @rpc
    def describe_configuration(self):
        """Describes the device configuration."""

    def get(self, cached=True):
        """
        Gets the device value.
        """

        is_signal = self._signal_info is not None
        if not cached or not is_signal:
            res = self._run(cached=False, fcn=self.get)
            if isinstance(res, dict) and res.get("type") == "namedtuple":
                par = namedtuple(self.name, res.get("fields"))
                return par(**res.get("values"))
            return res

        ret = self.read()
        if ret is None:
            return None
        return ret.get(self._signal_info.get("obj_name"), {}).get("value")

    @rpc
    def put(self, value: Any):
        """
        Puts the device value.
        """


class Device(OphydInterfaceBase):
    """
    Device (bluesky interface):
    * trigger
    * read
    * describe
    * stage
    * unstage
    * pause
    * resume
    """

    @rpc
    def configure(self, config: dict):
        """
        Configures the device.
        """

    @rpc
    def stop(self):
        """
        Stops the device.
        """

    @rpc
    def stage(self):
        """
        Stages the device. This method should normally not be called directly, but rather
        via the scan server.
        """

    @rpc
    def unstage(self):
        """
        Unstages the device. This method should normally not be called directly, but rather
        via the scan server.
        """

    @rpc
    def summary(self):
        """
        Provides a summary of the device, all associated signals and their type.
        """

    def __str__(self):
        # pylint: disable=import-outside-toplevel
        from bec_lib.devicemanager import DeviceManagerBase

        if isinstance(self.parent, DeviceManagerBase):
            config = "".join(
                [f"\t{key}: {val}\n" for key, val in self._config.get("deviceConfig").items()]
            )
            separator = "--" * 10
            return (
                f"{type(self).__name__}(name={self.name},"
                f" enabled={self.enabled}):\n{separator}\nDetails:\n\tDescription:"
                f" {self._config.get('description', self.name)}\n\tStatus:"
                f" {'enabled' if self.enabled else 'disabled'}\n\tRead only:"
                f" {self.read_only}\n\tSoftware Trigger: {self.software_trigger}\n\t"
                f"Last recorded value: {self.read(cached=True)}\n\tDevice"
                f" class: {self._config.get('deviceClass')}\n\treadoutPriority:"
                f" {self._config.get('readoutPriority')}\n\tDevice tags:"
                f" {self._config.get('deviceTags', [])}\n\tUser parameter:"
                f" {self._config.get('userParameter')}\n{separator}\nConfig:\n{config}"
            )
        return f"{type(self).__name__}(name={self.name}, enabled={self.enabled})"


class AdjustableMixin:
    @rpc
    def set(self, val):
        """
        Sets the device value.
        """
        pass

    @property
    def limits(self):
        """
        Returns the device limits.
        """
        limit_msg = self.root.parent.producer.get(MessageEndpoints.device_limits(self.root.name))
        if not limit_msg:
            return [0, 0]
        limit_msg = messages.DeviceMessage.loads(limit_msg)
        limits = [
            limit_msg.content["signals"].get("low", 0),
            limit_msg.content["signals"].get("high", 0),
        ]
        return limits

    @limits.setter
    def limits(self, val: list):
        self.update_config({"deviceConfig": {"limits": val}})

    @property
    def low_limit(self):
        """
        Returns the low limit.
        """
        return self.limits[0]

    @low_limit.setter
    def low_limit(self, val: float):
        limits = [val, self.high_limit]
        self.update_config({"deviceConfig": {"limits": limits}})

    @property
    def high_limit(self):
        """
        Returns the high limit.
        """
        return self.limits[1]

    @high_limit.setter
    def high_limit(self, val: float):
        limits = [self.low_limit, val]
        self.update_config({"deviceConfig": {"limits": limits}})


class Signal(AdjustableMixin, OphydInterfaceBase):
    pass


class Positioner(AdjustableMixin, Device):
    """
    Positioner:
    * trigger
    * read
    * set
    * stop
    * settle_time
    * timeout
    * egu
    * limits
    * low_limit
    * high_limit
    * move
    * position
    * moving
    """

    @rpc
    def stop(self):
        pass

    @rpc
    def settle_time(self):
        pass

    @rpc
    def timeout(self):
        pass

    @rpc
    def egu(self):
        pass

    def move(self, val: float, relative=False):
        return self.parent.parent.scans.mv(self, val, relative=relative)

    @rpc
    def position(self):
        pass

    @rpc
    def moving(self):
        pass
