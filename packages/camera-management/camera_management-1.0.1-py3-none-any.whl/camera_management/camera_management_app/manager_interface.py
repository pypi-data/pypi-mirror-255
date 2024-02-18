import atexit
import json
import os
import pathlib
import signal
import subprocess
import sys
import threading
import time

import requests
import tabulate
from flask import Flask, jsonify, render_template, request
from waitress import serve

from camera_management.dataclasses.general_dataclasses import VideoDevice
from camera_management.tools.config_tools import check_config, write_configuration_file
from camera_management.tools.create_description import get_descriptions
from camera_management.tools.system_analyzer import get_connected_cams


class ManagerApp(threading.Thread):
    """
    This is the main backend class.

    It tries to connect to all physically connected camera devices and creates sockets for each device.
    This class runs on port 8090. Each socket for each camera runs on the nextmost port (8091+).
    """

    def __init__(self, path_to_configs: pathlib.Path, autostart: bool = True, choose_cameras=False, port=8090, host="0.0.0.0"):
        """
        This is the main backend class.

        It tries to connect to all physically connected camera devices and creates sockets for each device.
        This class runs on port 8090. Each socket for each camera runs on the nextmost port (8091+).

        :param path_to_configs: The path to the configs of the camera you want to use.
        :param autostart: If set to true the manager will automatically start sockets for all cameras that are configured (meaning: all cameras it finds a config file for)
        :param choose_cameras: If set to true the manager will ask which cameras you want to start.
        """
        super().__init__(name="Manager")

        self._flask = Flask(__name__)
        self._subprocess_dict = {}
        self._port = port
        self._host = host
        self._path = path_to_configs
        self._configs = {}
        self._chosen_cameras = None
        self._cam_config_path = pathlib.Path(__file__).parent.parent / "camera_app/temp/"

        self.cam_status = []
        self.available_cameras = None

        if autostart and choose_cameras:
            raise ValueError("You can not use autostart and chose_cameras in conjunction.")

        if not autostart:
            if choose_cameras:
                self.available_cameras = self._get_video_device()
            else:
                while self.available_cameras is None:
                    time.sleep(1)
        else:
            self.available_cameras = get_connected_cams()

        @atexit.register
        def __exit():
            for key, value in self._subprocess_dict.items():
                os.kill(value.pid, signal.SIGTERM)

        @self._flask.get("/info")
        def get_camera_info():
            return jsonify(self.cam_status)

        @self._flask.get("/config")
        def get_cam_config():
            port = request.args.get("port", default=None, type=int)
            return jsonify(self._configs[port])

        @self._flask.get("/")
        def index():
            """
            Start page.
            """
            return render_template("index.html")

        @self._flask.get("/available_cams")
        def available_cams():
            """
            Get available cams.
            """
            cams = get_connected_cams()
            return jsonify([cam.to_dict() for cam in cams])

    def _wait_for_interface(self, port: int, timeout=10.0) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            try:
                status = requests.get(f"http://{self._host}:{str(port)}/status").json()
            except requests.ConnectionError:
                time.sleep(0.1)
                continue
            if status["status"] == "ONLINE":
                return True
            return False
        return False

    def _prepare_cam_descriptions(self):
        type_configs = get_descriptions(self._path / "type_configs/")
        individual_configs = get_descriptions(self._path / "individual_configs/")
        ignored_configs = []
        i = 1

        for cam in self.available_cameras:
            status = {
                "CAM TYPE": cam.product,
                "CAM SERIAL": None,
                "CONFIG TYPE": False,
                "CONFIG INDIVIDUAL": False,
                "PORT": None,
                "PORT ACTIVE": False,
                "CALIBRATION AVAILABLE": False,
            }

            for iconfig in individual_configs:
                if iconfig in ignored_configs:
                    continue
                with open(iconfig) as icfg:
                    json_icfg = json.load(icfg)

                json_icfg = check_config(json_icfg, mode="individual", config_path=iconfig)
                if json_icfg is None:
                    ignored_configs.append(iconfig)
                    continue

                if sys.platform.upper() == "DARWIN":
                    serial = cam.unique_id
                    json_serial = json_icfg.information.device.unique_id

                else:
                    serial = cam.serial
                    json_serial = json_icfg.information.device.serial

                status["CAM SERIAL"] = serial

                if json_serial == serial:
                    port = self._port + i
                    i += 1

                    json_icfg.information.device = cam
                    self._configs[port] = {"CONFIG TYPE": None, "CONFIG MODEL": json_icfg}
                    write_configuration_file(filename=f"{port}.json", cam_config_path=self._cam_config_path, content=json_icfg.model_dump())

                    self._subprocess_dict[port] = subprocess.Popen(
                        [sys.executable, f"{pathlib.Path(__file__).parent.parent / 'camera_app/camera_interface.py'}", f"{port}"]
                    )
                    status["CONFIG INDIVIDUAL"] = True
                    status["PORT"] = port
                    status["PORT ACTIVE"] = self._wait_for_interface(port)
                    status["CALIBRATION AVAILABLE"] = True
                    self.cam_status.append(status)
                    break

            if status["PORT"] is not None:
                continue

            for tconfig in type_configs:
                if tconfig in ignored_configs:
                    continue
                with open(tconfig) as tcfg:
                    json_tcfg = json.load(tcfg)

                json_tcfg = check_config(json_tcfg, "type", tconfig)

                if json_tcfg is None:
                    ignored_configs.append(tconfig)
                    continue

                serial = cam.serial
                status["CAM SERIAL"] = serial

                if json_tcfg.information.device.product == cam.product:
                    port = self._port + i
                    i += 1

                    json_tcfg.information.device = cam
                    self._configs[port] = {"CONFIG TYPE": json_tcfg, "CONFIG MODEL": None}
                    write_configuration_file(filename=f"{port}.json", cam_config_path=self._cam_config_path, content=json_tcfg.model_dump())
                    self._subprocess_dict[port] = subprocess.Popen(
                        [sys.executable, f"{pathlib.Path(__file__).parent.parent / 'camera_app/camera_interface.py'}", f"{port}"]
                    )
                    status["CONFIG TYPE"] = True
                    status["PORT"] = port
                    status["PORT ACTIVE"] = self._wait_for_interface(port)
                    status["CALIBRATION AVAILABLE"] = json_tcfg.calibration.available
                    self.cam_status.append(status)
                    break

    @staticmethod
    def _get_video_device() -> list[VideoDevice]:
        streams: list[VideoDevice] = get_connected_cams(verbose=True)
        idx = [int(x) for x in input("\nEnter the stream indeces seperated by whitespace: ").split()]
        return [streams[i] for i in idx]

    def run(self):
        """
        Runs the manager application.
        """

        self._prepare_cam_descriptions()
        if not self.cam_status:
            raise ValueError(f"No valid Camera Descriptions were found in {self._path}. Please provide a valid .json file.")

        serve(self._flask, host=self._host, port=self._port)

    def __str__(self) -> str:
        header = self.cam_status[0].keys()
        rows = [x.values() for x in self.cam_status]
        return tabulate.tabulate(rows, header)
