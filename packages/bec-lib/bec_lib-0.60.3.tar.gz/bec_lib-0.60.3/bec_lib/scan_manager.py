from __future__ import annotations

import uuid

from typeguard import typechecked

from bec_lib import messages
from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.queue_items import QueueStorage
from bec_lib.request_items import RequestStorage
from bec_lib.scan_items import ScanStorage

logger = bec_logger.logger


class ScanManager:
    def __init__(self, connector):
        """
        ScanManager is a class that provides a convenient way to interact with the scan queue as well
        as the requests and scans that are currently running or have been completed.
        It also contains storage container for the queue, requests and scans.

        Args:
            connector (BECConnector): BECConnector instance
        """
        self.connector = connector
        self.producer = self.connector.producer()
        self.queue_storage = QueueStorage(scan_manager=self)
        self.request_storage = RequestStorage(scan_manager=self)
        self.scan_storage = ScanStorage(scan_manager=self)

        self._scan_queue_consumer = self.connector.consumer(
            topics=MessageEndpoints.scan_queue_status(),
            cb=self._scan_queue_status_callback,
            parent=self,
        )
        self._scan_queue_request_consumer = self.connector.consumer(
            topics=MessageEndpoints.scan_queue_request(),
            cb=self._scan_queue_request_callback,
            parent=self,
        )
        self._scan_queue_request_response_consumer = self.connector.consumer(
            topics=MessageEndpoints.scan_queue_request_response(),
            cb=self._scan_queue_request_response_callback,
            parent=self,
        )
        self._scan_status_consumer = self.connector.consumer(
            topics=MessageEndpoints.scan_status(), cb=self._scan_status_callback, parent=self
        )

        self._scan_segment_consumer = self.connector.consumer(
            topics=MessageEndpoints.scan_segment(), cb=self._scan_segment_callback, parent=self
        )

        self._scan_queue_consumer.start()
        self._scan_queue_request_consumer.start()
        self._scan_queue_request_response_consumer.start()
        self._scan_status_consumer.start()
        self._scan_segment_consumer.start()

    def update_with_queue_status(self, queue: messages.ScanQueueStatusMessage) -> None:
        """update storage with a new queue status message"""
        self.queue_storage.update_with_status(queue)
        self.scan_storage.update_with_queue_status(queue)

    def request_scan_interruption(self, deferred_pause=True, scanID: str = None) -> None:
        """request a scan interruption

        Args:
            deferred_pause (bool, optional): Request a deferred pause. If False, a pause will be requested. Defaults to True.
            scanID (str, optional): ScanID. Defaults to None.

        """
        if scanID is None:
            scanID = self.scan_storage.current_scanID
        if not any(scanID):
            return self.request_scan_abortion()

        action = "deferred_pause" if deferred_pause else "pause"
        logger.info(f"Requesting {action}")
        return self.producer.send(
            MessageEndpoints.scan_queue_modification_request(),
            messages.ScanQueueModificationMessage(
                scanID=scanID, action=action, parameter={}
            ).dumps(),
        )

    def request_scan_abortion(self, scanID=None):
        """request a scan abortion

        Args:
            scanID (str, optional): ScanID. Defaults to None.

        """
        if scanID is None:
            scanID = self.scan_storage.current_scanID
        logger.info("Requesting scan abortion")
        self.producer.send(
            MessageEndpoints.scan_queue_modification_request(),
            messages.ScanQueueModificationMessage(
                scanID=scanID, action="abort", parameter={}
            ).dumps(),
        )

    def request_scan_halt(self, scanID=None):
        """request a scan halt

        Args:
            scanID (str, optional): ScanID. Defaults to None.

        """
        if scanID is None:
            scanID = self.scan_storage.current_scanID
        logger.info("Requesting scan halt")
        self.producer.send(
            MessageEndpoints.scan_queue_modification_request(),
            messages.ScanQueueModificationMessage(
                scanID=scanID, action="halt", parameter={}
            ).dumps(),
        )

    def request_scan_continuation(self, scanID=None):
        """request a scan continuation

        Args:
            scanID (str, optional): ScanID. Defaults to None.

        """
        if scanID is None:
            scanID = self.scan_storage.current_scanID
        logger.info("Requesting scan continuation")
        self.producer.send(
            MessageEndpoints.scan_queue_modification_request(),
            messages.ScanQueueModificationMessage(
                scanID=scanID, action="continue", parameter={}
            ).dumps(),
        )

    def request_queue_reset(self):
        """request a scan queue reset"""
        logger.info("Requesting a queue reset")
        self.producer.send(
            MessageEndpoints.scan_queue_modification_request(),
            messages.ScanQueueModificationMessage(
                scanID=None, action="clear", parameter={}
            ).dumps(),
        )

    def request_scan_restart(self, scanID=None, requestID=None, replace=True) -> str:
        """request to restart a scan"""
        if scanID is None:
            scanID = self.scan_storage.current_scanID
        if requestID is None:
            requestID = str(uuid.uuid4())
        logger.info("Requesting to abort and repeat a scan")
        position = "replace" if replace else "append"

        self.producer.send(
            MessageEndpoints.scan_queue_modification_request(),
            messages.ScanQueueModificationMessage(
                scanID=scanID, action="restart", parameter={"position": position, "RID": requestID}
            ).dumps(),
        )
        return requestID

    @property
    def next_scan_number(self):
        """get the next scan number from redis"""
        num = self.producer.get(MessageEndpoints.scan_number())
        if num is None:
            logger.warning("Failed to retrieve scan number from redis.")
            return -1
        return int(num)

    @next_scan_number.setter
    @typechecked
    def next_scan_number(self, val: int):
        """set the next scan number in redis"""
        return self.producer.set(MessageEndpoints.scan_number(), val)

    @property
    def next_dataset_number(self):
        """get the next dataset number from redis"""
        return int(self.producer.get(MessageEndpoints.dataset_number()))

    @next_dataset_number.setter
    @typechecked
    def next_dataset_number(self, val: int):
        """set the next dataset number in redis"""
        return self.producer.set(MessageEndpoints.dataset_number(), val)

    @staticmethod
    def _scan_queue_status_callback(msg, *, parent: ScanManager, **_kwargs) -> None:
        queue_status = messages.ScanQueueStatusMessage.loads(msg.value)
        if not queue_status:
            return
        parent.update_with_queue_status(queue_status)

    @staticmethod
    def _scan_queue_request_callback(msg, *, parent: ScanManager, **_kwargs) -> None:
        request = messages.ScanQueueMessage.loads(msg.value)
        parent.request_storage.update_with_request(request)

    @staticmethod
    def _scan_queue_request_response_callback(msg, *, parent: ScanManager, **_kwargs) -> None:
        response = messages.RequestResponseMessage.loads(msg.value)
        logger.debug(response)
        parent.request_storage.update_with_response(response)

    @staticmethod
    def _scan_status_callback(msg, *, parent: ScanManager, **_kwargs) -> None:
        scan = messages.ScanStatusMessage.loads(msg.value)
        parent.scan_storage.update_with_scan_status(scan)

    @staticmethod
    def _scan_segment_callback(msg, *, parent: ScanManager, **_kwargs) -> None:
        scan_msgs = messages.ScanMessage.loads(msg.value)
        if not isinstance(scan_msgs, list):
            scan_msgs = [scan_msgs]
        for scan_msg in scan_msgs:
            parent.scan_storage.add_scan_segment(scan_msg)

    def __repr__(self) -> str:
        return "\n".join(self.queue_storage.describe_queue())

    def shutdown(self):
        """stop the scan manager's threads"""
        self._scan_queue_consumer.shutdown()
        self._scan_queue_request_consumer.shutdown()
        self._scan_queue_request_response_consumer.shutdown()
        self._scan_status_consumer.shutdown()
        self._scan_segment_consumer.shutdown()
