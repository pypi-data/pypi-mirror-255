from __future__ import annotations

import time
import warnings
from functools import wraps
from typing import TYPE_CHECKING

import redis

from bec_lib.connector import (
    ConnectorBase,
    ConsumerConnector,
    ConsumerConnectorThreaded,
    MessageObject,
    ProducerConnector,
)
from bec_lib.endpoints import MessageEndpoints
from bec_lib.messages import AlarmMessage, BECMessage, LogMessage
from bec_lib.serialization import MsgpackSerialization

if TYPE_CHECKING:
    from bec_lib.alarm_handler import Alarms


def catch_connection_error(func):
    """catch connection errors"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.exceptions.ConnectionError:
            warnings.warn("Failed to connect to redis. Is the server running?")
            time.sleep(0.1)
            return None

    return wrapper


class RedisConnector(ConnectorBase):
    def __init__(self, bootstrap: list, redis_cls=None):
        super().__init__(bootstrap)
        self.redis_cls = redis_cls
        self.host, self.port = (
            bootstrap[0].split(":") if isinstance(bootstrap, list) else bootstrap.split(":")
        )
        self._notifications_producer = RedisProducer(
            host=self.host, port=self.port, redis_cls=self.redis_cls
        )

    def producer(self, **kwargs):
        return RedisProducer(host=self.host, port=self.port, redis_cls=self.redis_cls)

    # pylint: disable=too-many-arguments
    def consumer(
        self,
        topics=None,
        pattern=None,
        group_id=None,
        event=None,
        cb=None,
        threaded=True,
        name=None,
        **kwargs,
    ):
        if cb is None:
            raise ValueError("The callback function must be specified.")

        if threaded:
            if topics is None and pattern is None:
                raise ValueError("Topics must be set for threaded consumer")
            listener = RedisConsumerThreaded(
                self.host,
                self.port,
                topics,
                pattern,
                group_id,
                event,
                cb,
                redis_cls=self.redis_cls,
                name=name,
                **kwargs,
            )
            self._threads.append(listener)
            return listener
        return RedisConsumer(
            self.host,
            self.port,
            topics,
            pattern,
            group_id,
            event,
            cb,
            redis_cls=self.redis_cls,
            **kwargs,
        )

    def stream_consumer(
        self,
        topics=None,
        pattern=None,
        group_id=None,
        event=None,
        cb=None,
        from_start=False,
        newest_only=False,
        **kwargs,
    ):
        """
        Threaded stream consumer for redis streams.

        Args:
            topics (str, list): topics to subscribe to
            pattern (str, list): pattern to subscribe to
            group_id (str): group id
            event (threading.Event): event to stop the consumer
            cb (function): callback function
            from_start (bool): read from start. Defaults to False.
            newest_only (bool): read only the newest message. Defaults to False.
        """
        if cb is None:
            raise ValueError("The callback function must be specified.")

        if pattern:
            raise ValueError("Pattern is currently not supported for stream consumer.")

        if topics is None and pattern is None:
            raise ValueError("Topics must be set for stream consumer.")
        listener = RedisStreamConsumerThreaded(
            self.host,
            self.port,
            topics,
            pattern,
            group_id,
            event,
            cb,
            redis_cls=self.redis_cls,
            from_start=from_start,
            newest_only=newest_only,
            **kwargs,
        )
        self._threads.append(listener)
        return listener

    @catch_connection_error
    def log_warning(self, msg):
        """send a warning"""
        self._notifications_producer.send(
            MessageEndpoints.log(), LogMessage(log_type="warning", log_msg=msg)
        )

    @catch_connection_error
    def log_message(self, msg):
        """send a log message"""
        self._notifications_producer.send(
            MessageEndpoints.log(), LogMessage(log_type="log", log_msg=msg)
        )

    @catch_connection_error
    def log_error(self, msg):
        """send an error as log"""
        self._notifications_producer.send(
            MessageEndpoints.log(), LogMessage(log_type="error", log_msg=msg)
        )

    @catch_connection_error
    def raise_alarm(self, severity: Alarms, alarm_type: str, source: str, msg: str, metadata: dict):
        """raise an alarm"""
        self._notifications_producer.set_and_publish(
            MessageEndpoints.alarm(),
            AlarmMessage(
                severity=severity, alarm_type=alarm_type, source=source, msg=msg, metadata=metadata
            ),
        )


class RedisProducer(ProducerConnector):
    def __init__(self, host: str, port: int, redis_cls=None) -> None:
        # pylint: disable=invalid-name
        if redis_cls:
            self.r = redis_cls(host=host, port=port)
            return
        self.r = redis.Redis(host=host, port=port)
        self.stream_keys = {}

    def execute_pipeline(self, pipeline):
        """Execute the pipeline and returns the results with decoded BECMessages"""
        ret = []
        results = pipeline.execute()
        for res in results:
            try:
                ret.append(MsgpackSerialization.loads(res))
            except RuntimeError:
                ret.append(res)
        return ret

    @catch_connection_error
    def raw_send(self, topic: str, msg: bytes, pipe=None):
        """send to redis without any check on message type"""
        client = pipe if pipe is not None else self.r
        client.publish(topic, msg)

    def send(self, topic: str, msg: BECMessage, pipe=None) -> None:
        """send to redis"""
        if not isinstance(msg, BECMessage):
            raise TypeError(f"Message {msg} is not a BECMessage")
        self.raw_send(topic, MsgpackSerialization.dumps(msg), pipe)

    @catch_connection_error
    def lpush(
        self, topic: str, msg: str, pipe=None, max_size: int = None, expire: int = None
    ) -> None:
        """Time complexity: O(1) for each element added, so O(N) to
        add N elements when the command is called with multiple arguments.
        Insert all the specified values at the head of the list stored at key.
        If key does not exist, it is created as empty list before
        performing the push operations. When key holds a value that
        is not a list, an error is returned."""
        client = pipe if pipe is not None else self.pipeline()
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        client.lpush(topic, msg)
        if max_size:
            client.ltrim(topic, 0, max_size)
        if expire:
            client.expire(topic, expire)
        if not pipe:
            client.execute()

    @catch_connection_error
    def lset(self, topic: str, index: int, msg: str, pipe=None) -> None:
        client = pipe if pipe is not None else self.r
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        return client.lset(topic, index, msg)

    @catch_connection_error
    def rpush(self, topic: str, msg: str, pipe=None) -> int:
        """O(1) for each element added, so O(N) to add N elements when the
        command is called with multiple arguments. Insert all the specified
        values at the tail of the list stored at key. If key does not exist,
        it is created as empty list before performing the push operation. When
        key holds a value that is not a list, an error is returned."""
        client = pipe if pipe is not None else self.r
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        return client.rpush(topic, msg)

    @catch_connection_error
    def lrange(self, topic: str, start: int, end: int, pipe=None):
        """O(S+N) where S is the distance of start offset from HEAD for small
        lists, from nearest end (HEAD or TAIL) for large lists; and N is the
        number of elements in the specified range. Returns the specified elements
        of the list stored at key. The offsets start and stop are zero-based indexes,
        with 0 being the first element of the list (the head of the list), 1 being
        the next element and so on."""
        client = pipe if pipe is not None else self.r
        cmd_result = client.lrange(topic, start, end)
        if pipe:
            return cmd_result
        else:
            # in case of command executed in a pipe, use 'execute_pipeline' method
            ret = []
            for msg in cmd_result:
                try:
                    ret.append(MsgpackSerialization.loads(msg))
                except RuntimeError:
                    ret.append(msg)
            return ret

    @catch_connection_error
    def set_and_publish(self, topic: str, msg, pipe=None, expire: int = None) -> None:
        """piped combination of self.publish and self.set"""
        client = pipe if pipe is not None else self.pipeline()
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        client.publish(topic, msg)
        client.set(topic, msg)
        if expire:
            client.expire(topic, expire)
        if not pipe:
            client.execute()

    @catch_connection_error
    def set(self, topic: str, msg, pipe=None, expire: int = None) -> None:
        """set redis value"""
        client = pipe if pipe is not None else self.r
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        client.set(topic, msg, ex=expire)

    @catch_connection_error
    def keys(self, pattern: str) -> list:
        """returns all keys matching a pattern"""
        return self.r.keys(pattern)

    @catch_connection_error
    def pipeline(self):
        """create a new pipeline"""
        return self.r.pipeline()

    @catch_connection_error
    def delete(self, topic, pipe=None):
        """delete topic"""
        client = pipe if pipe is not None else self.r
        client.delete(topic)

    @catch_connection_error
    def get(self, topic: str, pipe=None):
        """retrieve entry, either via hgetall or get"""
        client = pipe if pipe is not None else self.r
        data = client.get(topic)
        if pipe:
            return data
        else:
            try:
                return MsgpackSerialization.loads(data)
            except RuntimeError:
                return data

    @catch_connection_error
    def xadd(self, topic: str, msg_dict: dict, max_size=None, pipe=None, expire: int = None):
        """
        add to stream

        Args:
            topic (str): redis topic
            msg_dict (dict): message to add
            max_size (int, optional): max size of stream. Defaults to None.
            pipe (Pipeline, optional): redis pipe. Defaults to None.
            expire (int, optional): expire time. Defaults to None.

        Examples:
            >>> redis.xadd("test", {"test": "test"})
            >>> redis.xadd("test", {"test": "test"}, max_size=10)
        """
        if pipe:
            client = pipe
        elif expire:
            client = self.pipeline()
        else:
            client = self.r

        for key, msg in msg_dict.items():
            msg_dict[key] = MsgpackSerialization.dumps(msg)

        if max_size:
            client.xadd(topic, msg_dict, maxlen=max_size)
        else:
            client.xadd(topic, msg_dict)
        if expire:
            client.expire(topic, expire)
        if not pipe and expire:
            client.execute()

    @catch_connection_error
    def get_last(self, topic: str, key="data"):
        """retrieve last entry from stream"""
        client = self.r
        try:
            _, msg_dict = client.xrevrange(topic, "+", "-", count=1)[0]
        except TypeError:
            return None
        else:
            msg_dict = {k.decode(): MsgpackSerialization.loads(msg) for k, msg in msg_dict.items()}

            if key is None:
                return msg_dict
            return msg_dict.get(key)

    @catch_connection_error
    def xread(
        self, topic: str, id: str = None, count: int = None, block: int = None, from_start=False
    ) -> list:
        """
        read from stream

        Args:
            topic (str): redis topic
            id (str, optional): id to read from. Defaults to None.
            count (int, optional): number of messages to read. Defaults to None.
            block (int, optional): block for x milliseconds. Defaults to None.
            from_start (bool, optional): read from start. Defaults to False.

        Returns:
            [list]: list of messages

        Examples:
            >>> redis.xread("test", "0-0")
            >>> redis.xread("test", "0-0", count=1)

            # read one message at a time
            >>> key = 0
            >>> msg = redis.xread("test", key, count=1)
            >>> key = msg[0][1][0][0]
            >>> next_msg = redis.xread("test", key, count=1)
        """
        client = self.r
        if from_start:
            self.stream_keys[topic] = "0-0"
        if topic not in self.stream_keys:
            if id is None:
                try:
                    msg = self.r.xrevrange(topic, "+", "-", count=1)
                    if msg:
                        self.stream_keys[topic] = msg[0][0]
                        out = {}
                        for key, val in msg[0][1].items():
                            out[key.decode()] = MsgpackSerialization.loads(val)
                        return [out]
                    self.stream_keys[topic] = "0-0"
                except redis.exceptions.ResponseError:
                    self.stream_keys[topic] = "0-0"
        if id is None:
            id = self.stream_keys[topic]

        msg = client.xread({topic: id}, count=count, block=block)
        return self._decode_stream_messages_xread(msg)

    def _decode_stream_messages_xread(self, msg):
        out = []
        for topic, msgs in msg:
            for index, record in msgs:
                out.append(
                    {k.decode(): MsgpackSerialization.loads(msg) for k, msg in record.items()}
                )
                self.stream_keys[topic] = index
        return out if out else None

    @catch_connection_error
    def xrange(self, topic: str, min: str, max: str, count: int = None):
        """
        read a range from stream

        Args:
            topic (str): redis topic
            min (str): min id. Use "-" to read from start
            max (str): max id. Use "+" to read to end
            count (int, optional): number of messages to read. Defaults to None.
        """
        client = self.r
        msgs = []
        for reading in client.xrange(topic, min, max, count=count):
            for index, msg_dict in record:
                msgs.append(
                    {k.decode(): MsgpackSerialization.loads(msg) for k, msg in msg_dict.items()}
                )
        return msgs


class RedisConsumerMixin:
    def _init_topics_and_pattern(self, topics, pattern):
        if topics:
            if not isinstance(topics, list):
                topics = [topics]
        if pattern:
            if not isinstance(pattern, list):
                pattern = [pattern]
        return topics, pattern

    def _init_redis_cls(self, redis_cls):
        # pylint: disable=invalid-name
        if redis_cls:
            self.r = redis_cls(host=self.host, port=self.port)
        else:
            self.r = redis.Redis(host=self.host, port=self.port)

    @catch_connection_error
    def initialize_connector(self) -> None:
        if self.pattern is not None:
            self.pubsub.psubscribe(self.pattern)
        else:
            self.pubsub.subscribe(self.topics)


class RedisConsumer(RedisConsumerMixin, ConsumerConnector):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        host,
        port,
        topics=None,
        pattern=None,
        group_id=None,
        event=None,
        cb=None,
        redis_cls=None,
        **kwargs,
    ):
        self.host = host
        self.port = port

        bootstrap_server = "".join([host, ":", port])
        topics, pattern = self._init_topics_and_pattern(topics, pattern)
        super().__init__(
            bootstrap_server=bootstrap_server,
            topics=topics,
            pattern=pattern,
            group_id=group_id,
            event=event,
            cb=cb,
            **kwargs,
        )
        self.error_message_sent = False
        self._init_redis_cls(redis_cls)
        self.pubsub = self.r.pubsub()
        self.initialize_connector()

    @catch_connection_error
    def poll_messages(self) -> None:
        """
        Poll messages from self.connector and call the callback function self.cb
        """
        message = self.pubsub.get_message(ignore_subscribe_messages=True)
        if message is not None:
            msg = MessageObject(
                topic=message["channel"], value=MsgpackSerialization.loads(message["data"])
            )
            return self.cb(msg, **self.kwargs)

        time.sleep(0.01)
        return None

    def shutdown(self):
        """shutdown the consumer"""
        self.pubsub.close()


class RedisStreamConsumerThreaded(RedisConsumerMixin, ConsumerConnectorThreaded):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        host,
        port,
        topics=None,
        pattern=None,
        group_id=None,
        event=None,
        cb=None,
        redis_cls=None,
        from_start=False,
        newest_only=False,
        **kwargs,
    ):
        self.host = host
        self.port = port
        self.from_start = from_start
        self.newest_only = newest_only

        bootstrap_server = "".join([host, ":", port])
        topics, pattern = self._init_topics_and_pattern(topics, pattern)
        super().__init__(
            bootstrap_server=bootstrap_server,
            topics=topics,
            pattern=pattern,
            group_id=group_id,
            event=event,
            cb=cb,
            **kwargs,
        )

        self._init_redis_cls(redis_cls)

        self.sleep_times = [0.005, 0.1]
        self.last_received_msg = 0
        self.idle_time = 30
        self.error_message_sent = False
        self.stream_keys = {}

    def initialize_connector(self) -> None:
        pass

    def _init_topics_and_pattern(self, topics, pattern):
        if topics:
            if not isinstance(topics, list):
                topics = [topics]
        if pattern:
            if not isinstance(pattern, list):
                pattern = [pattern]
        return topics, pattern

    def get_id(self, topic: str) -> str:
        """
        Get the stream key for the given topic.

        Args:
            topic (str): topic to get the stream key for
        """
        if topic not in self.stream_keys:
            return "0-0"
        return self.stream_keys.get(topic)

    def get_newest_message(self, container: list, append=True) -> None:
        """
        Get the newest message from the stream and update the stream key. If
        append is True, append the message to the container.

        Args:
            container (list): container to append the message to
            append (bool, optional): append to container. Defaults to True.
        """
        for topic in self.topics:
            msg = self.r.xrevrange(topic, "+", "-", count=1)
            if msg:
                if append:
                    container.append((topic, msg[0][1]))
                self.stream_keys[topic] = msg[0][0]
            else:
                self.stream_keys[topic] = "0-0"

    @catch_connection_error
    def poll_messages(self) -> None:
        """
        Poll messages from self.connector and call the callback function self.cb

        """
        if self.pattern is not None:
            topics = [key.decode() for key in self.r.scan_iter(match=self.pattern, _type="stream")]
        else:
            topics = self.topics
        messages = []
        if self.newest_only:
            self.get_newest_message(messages)
        elif not self.from_start and not self.stream_keys:
            self.get_newest_message(messages, append=False)
        else:
            streams = {topic: self.get_id(topic) for topic in topics}
            read_msgs = self.r.xread(streams, count=1)
            if read_msgs:
                for msg in read_msgs:
                    topic = msg[0].decode()
                    messages.append((topic, msg[1][0][1]))
                    self.stream_keys[topic] = msg[1][-1][0]

        if messages:
            if MessageEndpoints.log() not in topics:
                # no need to update the update frequency just for logs
                self.last_received_msg = time.time()
            for topic, msg in messages:
                try:
                    msg = MsgpackSerialization.loads(msg[b"data"])
                except RuntimeError:
                    msg = msg[b"data"]
                msg_obj = MessageObject(topic=topic, value=msg)
                self.cb(msg_obj, **self.kwargs)
        else:
            sleep_time = int(bool(time.time() - self.last_received_msg > self.idle_time))
            if self.sleep_times[sleep_time]:
                time.sleep(self.sleep_times[sleep_time])


class RedisConsumerThreaded(RedisConsumerMixin, ConsumerConnectorThreaded):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        host,
        port,
        topics=None,
        pattern=None,
        group_id=None,
        event=None,
        cb=None,
        redis_cls=None,
        name=None,
        **kwargs,
    ):
        self.host = host
        self.port = port

        bootstrap_server = "".join([host, ":", port])
        topics, pattern = self._init_topics_and_pattern(topics, pattern)
        super().__init__(
            bootstrap_server=bootstrap_server,
            topics=topics,
            pattern=pattern,
            group_id=group_id,
            event=event,
            cb=cb,
            name=name,
            **kwargs,
        )

        self._init_redis_cls(redis_cls)
        self.pubsub = self.r.pubsub()

        self.sleep_times = [0.005, 0.1]
        self.last_received_msg = 0
        self.idle_time = 30
        self.error_message_sent = False

    @catch_connection_error
    def poll_messages(self) -> None:
        """
        Poll messages from self.connector and call the callback function self.cb

        Note: pubsub messages are supposed to be BECMessage objects only
        """
        messages = self.pubsub.get_message(ignore_subscribe_messages=True)
        if messages is not None:
            if f"{MessageEndpoints.log()}".encode() not in messages["channel"]:
                # no need to update the update frequency just for logs
                self.last_received_msg = time.time()
            msg = MessageObject(
                topic=messages["channel"].decode(),
                value=MsgpackSerialization.loads(messages["data"]),
            )
            self.cb(msg, **self.kwargs)
        else:
            sleep_time = int(bool(time.time() - self.last_received_msg > self.idle_time))
            if self.sleep_times[sleep_time]:
                time.sleep(self.sleep_times[sleep_time])

    def shutdown(self):
        super().shutdown()
        self.pubsub.close()
