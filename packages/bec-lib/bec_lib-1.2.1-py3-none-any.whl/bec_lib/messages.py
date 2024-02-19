from __future__ import annotations

import dataclasses
import enum
import time
import warnings
from copy import deepcopy
from dataclasses import MISSING, dataclass, field, fields
from typing import Any, Literal

import numpy as np


class BECStatus(enum.Enum):
    """BEC status enum"""

    RUNNING = 2
    BUSY = 1
    IDLE = 0
    ERROR = -1


@dataclass
class BECMessage:

    def __post_init__(self):
        # in case "metadata" is passed None as keyword arg, for example
        for f in fields(self):
            value = getattr(self, f.name)
            if value is None and not f.default_factory is MISSING:
                setattr(self, f.name, f.default_factory())

    @property
    def content(self):
        content = self.__dict__.copy()  # dataclasses.asdict(self)
        content.pop("metadata", None)
        return content

    def _is_valid(self) -> bool:
        return True

    def __eq__(self, other):
        if not isinstance(other, BECMessage):
            # don't attempt to compare against unrelated types
            return False

        try:
            np.testing.assert_equal(self.__dict__, other.__dict__)
        except AssertionError:
            return False

        # remove the pylint disable when we upgrade to python 3.10. dataclasses will support kw_only
        # pylint: disable=no-member
        return self.msg_type == other.msg_type and self.metadata == other.metadata

    def __str__(self):
        return f"messages.{self.__class__.__name__}(**{self.content}, metadata={self.metadata})"

    def loads(self):
        warnings.warn(
            "BECMessage.loads() is deprecated and should not be used anymore. When calling Connector methods, it can be omitted. When a message needs to be deserialized call the appropriate function from bec_lib.serialization",
            FutureWarning,
        )
        return self

    def dumps(self):
        warnings.warn(
            "BECMessage.dumps() is deprecated and should not be used anymore. When calling Connector methods, it can be omitted. When a message needs to be serialized call the appropriate function from bec_lib.serialization",
            FutureWarning,
        )
        return self


@dataclass
class BundleMessage(BECMessage):
    """Bundle of BECMessages"""

    msg_type = "bundle_message"
    messages: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def append(self, msg: BECMessage):
        """append a new BECMessage to the bundle"""
        if not isinstance(msg, BECMessage):
            raise AttributeError(f"Cannot append message of type {msg.__class__.__name__}")
        else:
            self.messages.append(msg)

    def __len__(self):
        return len(self.messages)

    def __iter__(self):
        yield from self.messages


@dataclass(eq=False)
class ScanQueueMessage(BECMessage):
    """Message type for sending scan requests to the scan queue
    Sent by the API server / user to the scan_queue topic. It will be consumed by the scan server.
        Args:
            scan_type (str): one of the registered scan types; either rpc calls or scan types defined in the scan server
            parameter (dict): required parameters for the given scan_stype
            queue (str): either "primary" or "interception"
            metadata (dict, optional): additional metadata to describe the scan
        Examples:
            >>> ScanQueueMessage(scan_type="dscan", parameter={"motor1": "samx", "from_m1:": -5, "to_m1": 5, "steps_m1": 10, "motor2": "samy", "from_m2": -5, "to_m2": 5, "steps_m2": 10, "exp_time": 0.1})
    """

    msg_type = "scan_queue_message"
    scan_type: str
    parameter: dict
    queue: str = field(default="primary")
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ScanQueueHistoryMessage(BECMessage):
    """Sent after removal from the active queue. Contains information about the scan.
    Sent by the API server / user to the scan_queue topic. It will be consumed by the scan server.
    Args:
        status(str):  current scan status
        queueID(str): unique queue ID
        info(dict): dictionary containing additional information about the scan
        queue (str): either "primary" or "interception"
        metadata (dict, optional): additional metadata to describe the scan
    """

    msg_type = "queue_history"
    status: str
    queueID: str
    info: dict
    queue: str = field(default="primary")
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ScanStatusMessage(BECMessage):
    """Message type for sending scan status updates
    Args:
        scanID(str): unique scan ID
        status(dict): dictionary containing the current scan status
        info(dict): dictionary containing additional information about the scan
        timestamp(float, optional): timestamp of the scan status update. If None, the current time is used.
        metadata(dict, optional): additional metadata to describe and identify the scan.

    Examples:
        >>> ScanStatusMessage(scanID="1234", status={"scan_number": 1, "scan_motors": ["samx", "samy"], "scan_type": "dscan", "scan_status": "RUNNING"}, info={"positions": {"samx": 0.5, "samy": 0.5}})
    """

    msg_type = "scan_status"
    scanID: str
    status: dict
    info: dict
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    def __str__(self):
        content = deepcopy(self.__dict__)
        if content["info"].get("positions"):
            content["info"]["positions"] = "..."
        return f"{self.__class__.__name__}({content, self.metadata}))"


@dataclass(eq=False)
class ScanQueueModificationMessage(BECMessage):
    """Message type for sending scan queue modifications
    Args:
        scanID(str): unique scan ID
        action(str): one of the actions defined in ACTIONS
                     ("pause", "deferred_pause", "continue", "abort", "clear", "restart", "halt")
        parameter(dict): additional parameters for the action
        metadata(dict, optional): additional metadata to describe and identify the scan.
    """

    ACTIONS = ["pause", "deferred_pause", "continue", "abort", "clear", "restart", "halt"]
    msg_type = "scan_queue_modification"
    scanID: str
    action: str
    parameter: dict
    metadata: dict = field(default_factory=dict)

    def _is_valid(self) -> bool:
        return self.action in self.ACTIONS


@dataclass(eq=False)
class ScanQueueStatusMessage(BECMessage):
    """Message type for sending scan queue status updates
    Args:
        queue(dict): dictionary containing the current queue status
        metadata(dict, optional): additional metadata to describe and identify the scan.
    """

    msg_type = "scan_queue_status"
    queue: dict
    metadata: dict = field(default_factory=dict)

    def _is_valid(self) -> bool:
        if (
            not isinstance(self.queue, dict)
            or "primary" not in self.queue
            or not isinstance(self.queue["primary"], dict)
        ):
            return False
        return True


@dataclass(eq=False)
class RequestResponseMessage(BECMessage):
    """Message type for sending back decisions on the acceptance of requests
    Args:
        accepted (bool): True if the request was accepted
        message (str): String describing the decision, e.g. "Invalid request"
        metadata (dict, optional): additional metadata to describe and identify the request / response
    """

    msg_type = "request_response"
    accepted: bool
    message: str
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class DeviceInstructionMessage(BECMessage):
    """Message type for sending device instructions to the device server
    Args:
        device (str): device name
        action (str): device action, e.g. method call
        parameter (dict): device action parameter
        metadata (dict, optional): metadata to describe the conditions of the device instruction
    """

    msg_type = "device_instruction"
    device: str
    action: str
    parameter: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class DeviceMessage(BECMessage):
    """Message type for sending device readings from the device server
    Args:
        signals (dict): dictionary of device signals
        metadata (dict, optional): metadata to describe the conditions of the device reading
    Examples:
        >>> BECMessage.DeviceMessage(signals={'samx': {'value': 14.999033949016491, 'timestamp': 1686385306.0265112}, 'samx_setpoint': {'value': 15.0, 'timestamp': 1686385306.016806}, 'samx_motor_is_moving': {'value': 0, 'timestamp': 1686385306.026888}}}, metadata={'stream': 'primary', 'DIID': 353, 'RID': 'd3471acc-309d-43b7-8ff8-f986c3fdecf1', 'pointID': 49, 'scanID': '8e234698-358e-402d-a272-73e168a72f66', 'queueID': '7a232746-6c90-44f5-81f5-74ab0ea22d4a'})
    """

    msg_type = "device_message"
    signals: dict
    metadata: dict = field(default_factory=dict)

    def _is_valid(self) -> bool:
        return isinstance(self.signals, dict)


@dataclass(eq=False)
class DeviceRPCMessage(BECMessage):
    """Message type for sending device RPC return values from the device server
    Args:
        device (str): device name
        return_val (Any): return value of the RPC call
        out (str): output of the RPC call
        success (bool, optional): True if the RPC call was successful
        metadata (dict, optional): metadata to describe the conditions of the device RPC call
    """

    msg_type = "device_rpc_message"
    device: str
    return_val: Any
    out: str
    success: bool = field(default=True)
    metadata: dict = field(default_factory=dict)

    def _is_valid(self) -> bool:
        return isinstance(self.device, str)


@dataclass(eq=False)
class DeviceStatusMessage(BECMessage):
    """Message type for sending device status updates from the device server
    Args:
        device (str): device name
        status (int): device status
        metadata (dict, optional): additional metadata to describe the conditions of the device status
    """

    msg_type = "device_status_message"
    device: str
    status: int
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class DeviceReqStatusMessage(BECMessage):
    """Message type for sending device request status updates from the device server
    Args:
        device (str): device name
        success (bool): True if the request was successful
        metadata (dict, optional): additional metadata to describe the conditions of the device request status
    """

    msg_type = "device_req_status_message"
    device: str
    success: bool
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class DeviceInfoMessage(BECMessage):
    """Message type for sending device info updates from the device server
    Args:
        device (str): device name
        info (dict): device info as dictionary
        metadata (dict, optional): additional metadata to describe the conditions of the device info
    """

    msg_type = "device_info_message"
    device: str
    info: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class DeviceMonitorMessage(BECMessage):
    """Message type for sending device monitor updates from the device server
    Args:
        device (str): device name
        data (list): dictionary with device monitor data, #TODO should this be a list or better dictionary?
        metadata (dict, optional): additional metadata to describe the conditions of the device monitor
    """

    msg_type = "device_monitor_message"
    device: str
    data: np.ndarray
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ScanMessage(BECMessage):
    """Message type for sending scan segment data from the scan bundler
    Args:
        point_id (int): point ID from scan segment
        scanID (int): scan ID
        data (dict): scan segment data
        metadata (dict, optional): additional metadata to describe the conditions of the scan segment
    """

    msg_type = "scan_message"
    point_id: int
    scanID: int
    data: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ScanBaselineMessage(BECMessage):
    """Message type for sending scan baseline data from the scan bundler
    Args:
        scanID (int): scan ID
        data (dict): scan baseline data
        metadata (dict, optional): additional metadata to describe the conditions of the scan baseline
    """

    msg_type = "scan_baseline_message"
    scanID: int
    data: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class DeviceConfigMessage(BECMessage):
    """Message type for sending device config updates
    Args:
        action (str): set, update or reload
        config (dict): device config (add, set, update) or None (reload)
        metadata (dict, optional): additional metadata to describe the conditions of the device config
    """

    ACTIONS = ["add", "set", "update", "reload"]
    msg_type = "device_config_message"
    action: str
    config: dict
    metadata: dict = field(default_factory=dict)

    def _is_valid(self) -> bool:
        return self.action in self.ACTIONS


@dataclass(eq=False)
class LogMessage(BECMessage):
    """Log message
    Args:
        log_type (str): log, warning or error
        log_msg (dict or str): log message
        metadata (dict, optional):
    """

    msg_type = "log_message"
    log_type: str
    log_msg: dict | str
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class AlarmMessage(BECMessage):
    """Alarm message
    Severity 1: Minor alarm, no user interaction needed. The system can continue.
    Severity 2: Major alarm, user interaction needed. If the alarm was raised during the execution of a request, the request will be paused until the alarm is resolved.
    Severity 3: Major alarm, user interaction needed. The system cannot recover by itself.

    Args:
        severity (int): severity level (1-3)
        source (str): source of the problem (where did it occur?)
        msg (str): problem description (what happened?)
        metadata (dict, optional): Additional metadata.
    """

    msg_type = "alarm_message"
    severity: int
    alarm_type: str
    source: str
    msg: str
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class StatusMessage(BECMessage):
    """Status message
    Args:
        name (str): name of the status
        status (BECStatus): value of the BECStatus enum
        (RUNNING = 2
        BUSY = 1
        IDLE = 0
        ERROR = -1))
        info (dict): status info
        metadata (dict, optional): additional metadata
    """

    msg_type = "status_message"
    name: str
    status: BECStatus
    info: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class FileMessage(BECMessage):
    """File message to inform about the status of a file writing operation
    Args:
        file_path (str): path to the file
        done (bool, optional): True if the file writing operation is done. Defaults to True.
        successful (bool, optional): True if the file writing operation was successful. Defaults to True.
        metadata (dict, optional): status metadata. Defaults to None.
    """

    msg_type = "file_message"
    file_path: str
    done: bool = field(default=True)
    successful: bool = field(default=True)
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class FileContentMessage(BECMessage):
    """File content message to inform about the content of a file
    Args:
        file_path (str): path to the file
        data (str): content of the file
        metadata (dict, optional): status metadata. Defaults to None.
    """

    msg_type = "file_content_message"
    file_path: str
    data: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class VariableMessage(BECMessage):
    """Message to inform about a global variable
    Args:
        value (str): name of the global variable
        metadata (dict, optional): additional metadata
    """

    msg_type = "var_message"
    value: str
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ObserverMessage(BECMessage):
    """Message for observer updates
    Args:
        observer (list[dict]): list of observer descriptions (dictionaries)
        metadata (dict, optional): additional metadata
    """

    msg_type = "observer_message"
    observer: list[dict]
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ServiceMetricMessage(BECMessage):
    """Message for service metrics
    Args:
        name (str): name of the service
        metrics (dict): dictionary with service metrics
        metadata (dict, optional): additional metadata
    """

    msg_type = "service_metric_message"
    name: str
    metrics: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ProcessedDataMessage(BECMessage):
    """Message for processed data
    Args:
        data (str): processed data
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "processed_data_message"
    data: str
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class DAPConfigMessage(BECMessage):
    """Message for DAP configuration
    Args:
        config (dict): DAP configuration
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "dap_config_message"
    config: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class DAPRequestMessage(BECMessage):
    """Message for DAP requests
    Args:
        dap_cls (str): DAP class name
        dap_type (Literal["continuous", "on_demand"]): DAP type. Either "continuous" or "on_demand"
        config (dict): DAP configuration
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "dap_request_message"
    dap_cls: str
    dap_type: Literal["continuous", "on_demand"]
    config: dict
    metadata: dict = field(default_factory=dict)

    def _is_valid(self) -> bool:
        if self.dap_type not in ["continuous", "on_demand"]:
            return False
        return True


@dataclass(eq=False)
class DAPResponseMessage(BECMessage):
    """
    Message for DAP responses
    Args:
        success (bool): True if the request was successful
        data (dict, optional): DAP data. Defaults to None.
        error (dict, optional): DAP error. Defaults to None.
        dap_request (dict, optional): DAP request. Defaults to None.
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "dap_response_message"
    success: bool
    data: dict = field(default_factory=dict)
    error: dict = field(default_factory=dict)
    dap_request: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class AvailableResourceMessage(BECMessage):
    """Message for available resources such as scans, data processing plugins etc
    Args:
        resource (dict): resource description
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "available_resource_message"
    resource: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ProgressMessage(BECMessage):
    """Message for communicating the progress of a long running task
    Args:
        value (float): current progress value
        max_value (float): maximum progress value
        done (bool): True if the task is done
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "progress_message"
    value: float
    max_value: float
    done: bool
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class GUIConfigMessage(BECMessage):
    """Message for GUI configuration
    Args:
        config (dict): GUI configuration
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "gui_config_message"
    config: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class GUIDataMessage(BECMessage):
    """Message for GUI data
    Args:
        data (dict): GUI data
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "gui_data_message"
    data: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class GUIInstructionMessage(BECMessage):
    """Message for GUI instructions
    Args:
        instruction (str): GUI instruction
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "gui_instruction_message"
    action: str
    parameter: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class ServiceResponseMessage(BECMessage):
    """Message for service responses
    Args:
        response (dict): service response
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "service_response_message"
    response: dict
    metadata: dict = field(default_factory=dict)


@dataclass(eq=False)
class CredentialsMessage(BECMessage):
    """Message for credentials
    Args:
        credentials (dict): credentials
        metadata (dict, optional): metadata. Defaults to None.
    """

    msg_type = "credentials_message"
    credentials: dict
    metadata: dict = field(default_factory=dict)
