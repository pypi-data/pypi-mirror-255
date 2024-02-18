# pylint: disable = missing-module-docstring
from __future__ import annotations

import builtins
import importlib
import json
import select
import subprocess
import time
import uuid

from typeguard import typechecked

from bec_lib import BECClient, MessageEndpoints, messages

DEFAULT_CONFIG = {
    "plot_settings": {
        "background_color": "white",
        "axis_width": 2,
        "num_columns": 5,
        "colormap": "plasma",
        "scan_types": False,
    },
    "plot_data": [
        {
            "plot_name": "BPM4i plots vs samx",
            "x_label": "Motor Y",
            "y_label": "bpm4i",
            "sources": [
                {
                    "type": "scan_segment",
                    "signals": {"x": [{"name": "samx"}], "y": [{"name": "bpm4i"}]},
                },
                # {
                #     "type": "redis",
                #     "endpoint": "<redis_endpoint>",
                #     "update": "append",
                #     "signals": {
                #         "x": [{"name": "tag_x"}],
                #         "y": [{"name": "tag_y1"}, {"name": "tag_y2"}],
                #     },
                # },
            ],
        }
    ],
}


class BECWidgetsConnector:
    """
    A class to connect to the BEC widgets.
    """

    def __init__(self, gui_id: str, bec_client: BECClient = None) -> None:
        self._client = bec_client
        self.gui_id = gui_id
        # TODO replace with a global producer
        if self._client is None:
            if "bec" in builtins.__dict__:
                self._client = builtins.bec
            else:
                self._client = BECClient()
                self._client.start()
        self._producer = self._client.connector.producer()

    def set_plot_config(self, plot_id: str, config: dict) -> None:
        """
        Set the plot config.

        Args:
            plot_id (str): The id of the plot.
            config (dict): The config to set.
        """
        msg = messages.GUIConfigMessage(config=config)
        self._producer.set_and_publish(MessageEndpoints.gui_config(plot_id), msg)

    def close(self, plot_id: str) -> None:
        """
        Close the plot.

        Args:
            plot_id (str): The id of the plot.
        """
        msg = messages.GUIInstructionMessage(action="close", parameter={})
        self._producer.set_and_publish(MessageEndpoints.gui_instructions(plot_id), msg)

    def config_dialog(self, plot_id: str) -> None:
        """
        Open the config dialog.

        Args:
            plot_id (str): The id of the plot.
        """
        msg = messages.GUIInstructionMessage(action="config_dialog", parameter={})
        self._producer.set_and_publish(MessageEndpoints.gui_instructions(plot_id), msg)

    def send_data(self, plot_id: str, data: dict) -> None:
        """
        Send data to the plot.

        Args:
            plot_id (str): The id of the plot.
            data (dict): The data to send.
        """
        msg = messages.GUIDataMessage(data=data)
        self._producer.set_and_publish(topic=MessageEndpoints.gui_data(plot_id), msg=msg)
        # TODO bec_dispatcher can only handle set_and_publish ATM
        # self._producer.xadd(topic=MessageEndpoints.gui_data(plot_id),msg= {"data": msg})

    def clear(self, plot_id: str) -> None:
        """
        Clear the plot.

        Args:
            plot_id (str): The id of the plot.
        """
        msg = messages.GUIInstructionMessage(action="clear", parameter={})
        self._producer.set_and_publish(MessageEndpoints.gui_instructions(plot_id), msg)


class BECPlotter:
    """
    A class to plot data from the BEC. Internally, it uses redis to communicate with the plot running
    in a separate process.
    """

    def __init__(
        self, name: str, plot_id: str = None, widget_connector=None, default_config: dict = None
    ) -> None:
        """
        Initialize the BECPlotter.

        Args:
            name (str): The name of the plot.
            widget_connector (BECWidgetsConnector, optional): The plot connector to use. Defaults to None.
            default_config (dict, optional): The default config to use. Defaults to None.
            bec_client (BECClient, optional): The BECClient to use. Defaults to None.
        """
        self.name = name
        # Generate a unique id for the plot to be used in redis
        self._plot_id = plot_id if plot_id is not None else str(uuid.uuid4())
        self._config = default_config if default_config is not None else DEFAULT_CONFIG
        self.plot_connector = (
            widget_connector if widget_connector is not None else BECWidgetsConnector(self._plot_id)
        )

        self._process = None
        self._xdata = {}
        self._ydata = {}
        self._data_changed = False
        self._config_changed = False

    @typechecked
    def set_xlabel(self, xlabel: str, subplot: int = 0) -> None:
        """
        Set the xlabel of the figure.

        Args:
            xlabel (str): The xlabel to set.
            subplot (int, optional): The subplot to set the xlabel for. Defaults to 0.
        """
        self._config["plot_data"][subplot]["x_label"] = xlabel
        self._config_changed = True

    @typechecked
    def set_ylabel(self, ylabel: str, subplot: int = 0) -> None:
        """
        Set the ylabel of the figure.

        Args:
            ylabel (str): The ylabel to set.
            subplot (int, optional): The subplot to set the ylabel for. Defaults to 0.
        """
        self._config["plot_data"][subplot]["y_label"] = ylabel
        self._config_changed = True

    @typechecked
    def set_xsource(self, source: str, subplot: int = 0, source_order: int = 0) -> None:
        """
        Set the source of the xdata of the figure.

        Args:
            source (str): The source to set. Must be either a valid device name
            subplot (int, optimal): The subplot to change the xsource. Defaults to 0.
            source_order (int, optional): Which source to be changed. Defaults to 0.
        """
        self._config["plot_data"][subplot]["sources"][source_order]["signals"]["x"][0][
            "name"
        ] = source
        self._config_changed = True

    @typechecked
    def set_ysource(
        self, source: str, subplot: int = 0, source_order: int = 0, curve: int = 0
    ) -> None:
        """
        Set the source of the ydata of the figure.

        Args:
            source (str): The source to set. Must be either a valid device name
            subplot (int, optional): The subplot to set the ydata for. Defaults to 0.
            source_order (int, optional): Which source to be changed. Defaults to 0.
            curve (int, optional): The curve of the source. Defaults to 0.
        """
        self._config["plot_data"][subplot]["sources"][source_order]["signals"]["y"][curve][
            "name"
        ] = source
        self._config_changed = True

    @typechecked
    def set_xdata(
        self, data: list[float], tag: str = "x_default_tag", subplot_index: int = 0
    ) -> None:
        """
        Set the xdata of the figure using a specified tag.

        Args:
            data (list[float]): The xdata to set.
            tag (str): A tag to identify the xdata set in the config. Defaults to 'x_default_tag'.
            subplot_index (int, optional): The index of the subplot. Defaults to 0.
        """
        self._set_source_to_redis("x", tag, subplot_index)
        self._xdata = {"action": "set", "data": data, "tag": tag}
        self._data_changed = True

    @typechecked
    def set_ydata(
        self, data: list[float], tag: str = "y_default_tag", subplot_index: int = 0
    ) -> None:
        """
        Set the ydata of the figure for a specific curve, identified by a tag.

        Args:
            data (list[float]): The ydata to set for the curve.
            tag (str): A tag to identify the ydata set in the config and in plot legend. Defaults to 'y_default_tag'.
            subplot_index (int, optional): The index of the subplot. Defaults to 0.
        """
        self._set_source_to_redis("y", tag, subplot_index)
        self._ydata[tag] = {"action": "set", "data": data}
        self._data_changed = True

    @typechecked
    def set_xydata(
        self,
        xdata: list[float],
        ydata: list[float],
        xtag: str = "x_default_tag",
        ytag: str = "y_default_tag",
        subplot_index: int = 0,
    ) -> None:
        """
        Set both xdata and ydata of the figure.

        Args:
            xdata (list[float]): The xdata to set.
            ydata (list[float]): The ydata to set.
            xtag (str): A tag to identify the xdata set in the config. Defaults to 'x_default_tag'.
            ytag (str): A tag to identify the ydata set in the config and in plot legend. Defaults to 'y_default_tag'.
            subplot_index (int, optional): The index of the subplot. Defaults to 0.
        """
        if len(xdata) != len(ydata):
            print("Error: The lengths of x and y data do not match.")
            return

        self.set_xdata(xdata, xtag, subplot_index)
        self.set_ydata(ydata, ytag, subplot_index)

    def _set_source_to_redis(self, axis: str, tag: str = "tag", subplot_index: int = 0) -> None:
        """
        Ensure a 'redis' source exists in the configuration with the correct signals for the specified axis and subplot.

        Args:
            axis (str): The axis ('x' or 'y') to set the source for. Defaults to 'tag'.
            subplot_index (int, optional): The index of the subplot. Defaults to 0.
        """
        redis_source = next(
            (
                src
                for src in self._config["plot_data"][subplot_index]["sources"]
                if src.get("type") == "redis"
            ),
            None,
        )

        if not redis_source:
            redis_signals = {
                "x": [{"name": tag}] if axis == "x" else [],
                "y": [{"name": tag}] if axis == "y" else [],
            }
            redis_source = {
                "type": "redis",
                "endpoint": MessageEndpoints.gui_data(self._plot_id),
                "update": "append",
                "signals": redis_signals,
            }
            self._config["plot_data"][subplot_index]["sources"].append(redis_source)
        else:
            if axis == "x":
                redis_source["signals"]["x"] = [{"name": tag}]
            elif axis == "y":
                if not any(d["name"] == tag for d in redis_source["signals"]["y"]):
                    redis_source["signals"]["y"].append({"name": tag})

        self._config_changed = True

    @typechecked
    def append_xdata(
        self, xdata: float | list[float], tag: str = "x_default_tag", subplot_index: int = 0
    ) -> None:
        """
        Append xdata to the figure.

        Args:
            xdata (float | list[float]): The xdata to append.
            tag (str): A tag to identify the xdata set in the config. Defaults to 'x_default_tag'.
            subplot_index (int, optional): The index of the subplot. Defaults to 0.
        """
        self._set_source_to_redis("x", tag, subplot_index)
        self._xdata = {"action": "append", "data": xdata, "tag": tag}
        self._data_changed = True

    @typechecked
    def append_ydata(
        self, data: float | list[float], tag: str = "y_default_tag", subplot_index: int = 0
    ) -> None:
        """
        Append ydata to a specific curve in the figure, identified by a tag.

        Args:
            data (float | list[float]): The ydata to append to the curve.
            tag (str): A tag to identify the ydata set in the config and in plot legend. Defaults to 'y_default_tag'.
            subplot_index (int, optional): The index of the subplot. Defaults to 0.
        """
        self._set_source_to_redis("y", tag, subplot_index)
        self._ydata[tag] = {"action": "append", "data": data}
        self._data_changed = True

    @typechecked
    def append_xydata(
        self,
        xdata: list[float],
        ydata: list[float],
        xtag: str = "x_default_tag",
        ytag: str = "y_default_tag",
        subplot_index: int = 0,
    ) -> None:
        """
        Append the xdata and ydata to the figure. If xdata or ydata is a list, it the existing data will be extended
        by xdata or ydata.

        Args:
            xdata (list[float]): The xdata to set.
            ydata (list[float]): The ydata to set.
            xtag (str): A tag for the xdata set. Defaults to 'x_default_tag'.
            ytag (str): A tag for the ydata set. Defaults to 'y_default_tag'.
            subplot_index (int, optional): The index of the subplot. Defaults to 0.
        """
        if len(xdata) != len(ydata):
            print("Error: The lengths of x and y data do not match.")
            return

        self.append_xdata(xdata, xtag, subplot_index)
        self.append_ydata(ydata, ytag, subplot_index)

    def get_buffer_data(self):
        """Prints buffer data from BECPlotter."""
        print(70 * "-")
        print(f"xdata:{self._xdata}")
        print(70 * "-")
        print(f"ydata:{self._ydata}")
        print(70 * "-")

    def clear(self) -> None:
        """
        Clear the figure.
        """
        self.plot_connector.clear(self._plot_id)

    def config_dialog(self) -> None:
        """
        Clear the figure.
        """
        self.plot_connector.config_dialog(self._plot_id)

    def refresh(self) -> None:
        """
        Refresh the figure. Ensure data lengths match for each ydata set.
        """
        if self._config_changed:
            self.plot_connector.set_plot_config(self._plot_id, self._config)
            self._config_changed = False

        time.sleep(0.1)
        if self._data_changed:
            x_length = len(self._xdata.get("data", []))
            valid_ydata = {
                tag: ydata
                for tag, ydata in self._ydata.items()
                if len(ydata.get("data", [])) == x_length
            }

            if valid_ydata:
                data = {"x": self._xdata, "y": self._ydata}
                self.plot_connector.send_data(self._plot_id, data)
                self._data_changed = False
                self._xdata = {}
                self._ydata = {}
            else:
                print("Error: The lengths of x and y data do not match for all curves.")

    def show(self) -> None:
        """
        Show the figure.
        """
        if self._process is None or self._process.poll() is not None:
            self._start_plot_process()

    def close(self) -> None:
        """
        Close the figure.
        """
        if self._process is None:
            return
        self.plot_connector.close(self._plot_id)
        self._process.kill()
        self._process = None

    def _start_plot_process(self) -> None:
        """
        Start the plot in a new process.
        """
        # pylint: disable=subprocess-run-check
        monitor_module = importlib.import_module("bec_widgets.widgets.monitor.monitor")
        monitor_path = monitor_module.__file__

        command = (
            f"python {monitor_path} --id {self._plot_id} --config '{json.dumps(self._config)}'"
        )
        self._process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def print_log(self) -> None:
        """
        Print the log of the plot process.
        """
        if self._process is None:
            return
        print(self._get_stderr_output())

    def _get_stderr_output(self) -> str:
        stderr_output = []
        while self._process.poll() is not None:
            readylist, _, _ = select.select([self._process.stderr], [], [], 0.1)
            if not readylist:
                break
            line = self._process.stderr.readline()
            if not line:
                break
            stderr_output.append(line.decode("utf-8"))
        return "".join(stderr_output)

    def __del__(self) -> None:
        self.close()


if __name__ == "__main__":  # pragma: no cover
    plotter = BECPlotter("test")

    plotter.set_xlabel("xlabel")
    plotter.set_ylabel("ylabel")
    plotter.set_xydata(xdata=[1, 2, 3], ydata=[1, 2, 3])
    plotter.refresh()

    # or just
    # plotter.plot(xlabel="xlabel", ylabel="ylabel", xdata=[1, 2, 3], ydata=[1, 2, 3])

    plotter.show()
    plotter.close()
