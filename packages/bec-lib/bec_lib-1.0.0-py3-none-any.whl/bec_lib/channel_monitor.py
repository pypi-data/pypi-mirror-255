import argparse
import json
import threading

from bec_lib import messages
from bec_lib.redis_connector import RedisConnector
from bec_lib.service_config import ServiceConfig


def channel_callback(msg, **_kwargs):
    """
    Callback for channel monitor.
    """
    msg = msg.value
    out = {"msg_type": msg.msg_type, "content": msg.content, "metadata": msg.metadata}
    print(json.dumps(out, indent=4, default=lambda o: "<not serializable object>"))


def _start_consumer(config_path, topic):
    config = ServiceConfig(config_path)
    connector = RedisConnector(config.redis)
    consumer = connector.consumer(topics=topic, cb=channel_callback)
    consumer.start()
    event = threading.Event()
    event.wait()


def channel_monitor_launch():
    """
    Launch a channel monitor for a given channel.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", default="", help="path to the config file")
    parser.add_argument(
        "--channel", required=True, help="channel name, e.g. internal/devices/read/samx"
    )
    clargs = parser.parse_args()
    config_path = clargs.config
    topic = clargs.channel

    _start_consumer(config_path, topic)
