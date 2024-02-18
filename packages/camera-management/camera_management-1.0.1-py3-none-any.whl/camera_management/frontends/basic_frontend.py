from __future__ import annotations

import json
import logging
import time

import cv2
import requests
import tabulate

from camera_management import SETTINGS
from camera_management.dataclasses.aruco_dataclasses import ArucoParaSet
from camera_management.dataclasses.camera_dataclasses import CameraDescription, PreprocessingSettings
from camera_management.dataclasses.general_dataclasses import ImageProcessorData, MeasurementData, VideoDevice
from camera_management.frontends import _receiver

logger = logging.getLogger("camera_management.basic_frontend")


class manager_interface:
    def __init__(self, host="127.0.0.1", port=8090, autostart=True, timeout=10):
        """
        Frontend class to connect to manager backend.

        :param host: IP Adress of backend host you want to connect to.
        :param port: Port of backend host you want to connect to.
        :param autostart: If true, the manager starts the frontend interfaces for every backend camera interface automatically.
        :param timeout: How long the manager will wait for the backend camera interfaces to boot up.

        """
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}"
        self.camera_interfaces = []
        infos = self.get_configured_cams(timeout=timeout)  # this is here to ensure that the server is up

        if autostart:
            for info in infos:
                self.camera_interfaces.append((basic_Interface(host=self.host, port=int(info["PORT"])), int(info["PORT"])))
                logger.info(self.camera_interfaces[-1][0])

    def get_interface_by_index(self, idx: int) -> basic_Interface:
        """
        Get a camera by its index in the internal list of interfaces.
        """
        return self.camera_interfaces[idx][0]

    def get_interface_by_port(self, port: int) -> basic_Interface:
        """
        Get a camera interface by its port number (normally starting from 8091)
        """
        active = []
        for interface in self.camera_interfaces:
            active.append(interface[1])
            if interface[1] == port:
                return interface[0]
        raise ValueError(f"Port {port} is not a valid port. Current active ports are: {active}")

    def get_available_cams(self) -> list[VideoDevice]:
        """
        Returns a list of all the available cams the camera manager knows about (usually all connected cams).

        :param verbose: Also prints the list if set to true
        :return: List of available cams
        """
        cams = []
        try:
            response = requests.get(self.base_url + "/available_cams")
            for cam_json in response.json():
                cam = VideoDevice(**cam_json)
                cams.append(cam)

            logger.debug(f"All available cams for {self.base_url} are:")
            for cam in cams:
                logger.debug(f"\t{cam.product} @ {cam.path}")
            return cams

        except ConnectionError as ce:
            logger.warning(f"{ce.strerror}, please start the REST-API Application or connect network.")
            return []

    def get_configured_cams(self, timeout=1) -> list[dict]:
        """
        Returns a list of all the  cams the camera manager currently handles and their status.

        :param timeout: How long the function should wait for a response from the backend.
        :return: List of handled cams
        """
        start = time.time()
        while time.time() - start < timeout:
            try:
                response = requests.get(self.base_url + "/info")
                cam_status = response.json()

                logger.info(f"All handled cams for {self.base_url} are:{self._str_helper(cam_status)}")

                if cam_status is None:
                    raise OSError("There are no cameras to connect to.")
                return cam_status
            except requests.ConnectionError:
                continue
        raise OSError("There are no cams to connect to.")

    @staticmethod
    def _str_helper(infos: list[dict]) -> str:
        header = infos[0].keys()
        rows = [x.values() for x in infos]
        return tabulate.tabulate(rows, list(header))

    def __str__(self) -> str:
        infos = self.get_configured_cams()
        return self._str_helper(infos)


class basic_Interface:
    """
    A basic interface to get data from and configure a camera stream.
    """

    def __init__(self, host="127.0.0.1", port=8091):
        """
        A basic interface to get data from and configure a camera stream.

        :param host: The host IP address.
        :param port: The host port.
        :param log_cb: Callback function for logging !!! NOT YET IMPLEMENTED !!!
        :param data_cb: Callback function for calculated data !!! NOT YET IMPLEMENTED !!!
        :param stream_cb: Callback for the actual video stream.
        :param bw: Should the stream be black and white or color?
        :param undistort: Should the stream be distorted? (Only applicable if the camera config .json has calibration values)
        :param rotate: Rotates the image in 90 degree steps.
        """
        self.host = host
        self.port = port

        self.base_url = f"http://{self.host}:{self.port}"
        self.last_log_index = -1
        self.headers = {"Content-type": "application/json", "Accept": "application/json"}

        # self.log_rcv = receiver.LogReceiver(
        #     url=f"{self.base_url}/log",
        #     cb=self._update_log,
        # )

        self.stream_rcv = _receiver.ImageReceiver(
            url=f"{self.base_url}/data/imageProcessor",
        )
        # self.stream_infos = self.stream_rcv.stream_infos

        self.data_rcv = _receiver.PDReceiver(url=f"{self.base_url}/data/processed")
        # self.log_rcv.start()
        self.stream_rcv.start()
        self.data_rcv.start()

    def fetch_image_data(self) -> ImageProcessorData:
        """
        Returns the newest image of the camera stream.
        """
        return self.stream_rcv.fetch_data()

    def fetch_measurement_data(self) -> MeasurementData:
        """
        Returns the newest measurements of the camera stream.
        """
        return self.data_rcv.fetch_data()

    def _general_pre_proc_getter(self) -> PreprocessingSettings | None:
        resp = requests.get(f"{self.base_url}/settings/pre_processing")
        if resp.status_code != 200:
            logging.warning(f"Something went wrong while fetching pre processing settings. (HTTP Error Code {resp.status_code})")
            logging.warning(f"Error Message: {resp.content}")
            return None
        else:
            preprocessing_settings = PreprocessingSettings.model_validate(resp.json())
            return preprocessing_settings

    def _general_pre_proc_setter(self, arg: dict):
        resp = requests.post(
            f"{self.base_url}/settings/pre_processing",
            json.dumps(arg),
            headers=self.headers,
        )
        if resp.status_code != 200:
            logging.warning(f"Something went wrong while applying setting. (HTTP Error Code {resp.status_code}). Error: {resp.content}")

    def __str__(self):
        return f"basic_Interface listening on {self.base_url}"

    @property
    def rotate(self) -> int:
        """
        Image rotate setting of the camera stream.

        """
        return self._general_pre_proc_getter().rotate

    @rotate.setter
    def rotate(self, value: bool):
        if not isinstance(value, int) or value not in [0, 90, 180, 270]:
            logger.warning(f'{value} is of type {type(value)}. Only int values in [0, 90, 180, 270] are allowed for "rotate" setting.')
        else:
            self._rotate = value
            resp = requests.post(
                f"{self.base_url}/settings/pre_processing",
                json.dumps({"rotate": value}),
                headers=self.headers,
            )
            if resp.status_code != 200:
                logger.warning(f'Something went wrong while applying "rotate" setting. (HTTP Error Code {resp.status_code})')

    def get_general_setting(self, argument: cv2.CAP_PROP_SETTINGS) -> dict | None:
        """
        Gets the currently configured setting for the chosen argument.

        :param argument: The setting you want to query. Use cv2.CAP_xxx arguments.
        :return: A dict containing the argument and the current value.
        """
        if isinstance(argument, SETTINGS):
            argument = argument.value
        resp = requests.get(f"{self.base_url}/settings/camera", params={"settings": argument})
        if resp.status_code != 200:
            logger.warning(f"Something went wrong while fetching general setting. (HTTP Error Code {resp.status_code})")
            logger.warning(f"Error Message: {resp.content}")
            return {"Error": resp.content}
        else:
            return resp.json()

    def set_general_setting(self, argument: SETTINGS | int, value) -> str:
        """
        Sets the currently configured setting for the chosen argument.

        :param argument: The setting you want to query. Use cv2.CAP_xxx arguments.
        :param val: The value you want to set.
        """
        if isinstance(argument, SETTINGS):
            argument = argument.value
        resp = requests.post(f"{self.base_url}/settings/camera", json.dumps({"settings": (argument, value)}))
        if resp.status_code != 200:
            logger.warning(f"Something went wrong while applying general setting. (HTTP Error Code {resp.status_code})")
            logger.warning(f"Error Message: {resp.content}")
            return f"Error: {resp.content}"

        else:
            return resp.content.decode("utf-8")

    @property
    def description(self) -> dict:
        """
        Get the current configuration of the Camera.

        :return: A json-style representation of the calibration.
        """
        resp = requests.get(f"{self.base_url}/description")
        if resp.status_code != 200:
            logger.warning(f"Something went wrong while fetching configuration setting. (HTTP Error Code {resp.status_code}). Error: {resp.content}")
            logger.warning(f"Error Message: {resp.content}")
            return {"Error": resp.content}
        else:
            return resp.json()

    @description.setter
    def description(self, config: CameraDescription):
        # TODO: Make setter
        pass

    @property
    def undistort(self) -> bool:
        """
        Distortion setting of the camera stream.

        """
        return self._general_pre_proc_getter().undistort

    @undistort.setter
    def undistort(self, value: bool):
        if not isinstance(value, bool):
            logger.warning(f'{value} is of type {type(value)}. Only boolean values are allowed for "undistort" setting.')
        else:
            self._general_pre_proc_setter({"undistort": value})

    @property
    def bw(self) -> bool:
        """
        Black and white setting of the camera stream.

        """
        return self._general_pre_proc_getter().bw

    @bw.setter
    def bw(self, value: bool):
        if not isinstance(value, bool):
            logger.warning(f'{value} is of type {type(value)}. Only boolean values are allowed for "Black and White" setting.')
        else:
            self._general_pre_proc_setter({"bw": value})

    @property
    def aruco_active(self) -> bool:
        """
        Black and white setting of the camera stream.

        """
        return self._general_pre_proc_getter().aruco.active

    @aruco_active.setter
    def aruco_active(self, value: bool):
        if not isinstance(value, bool):
            logging.warning(f'{value} is of type {type(value)}. Only boolean values are allowed for "aruco.active" setting.')
        else:
            self._general_pre_proc_setter({"aruco": {"active": value}})

    @property
    def aruco_draw_active(self) -> bool:
        """
        Black and white setting of the camera stream.

        """
        return self._general_pre_proc_getter().aruco.draw_active

    @aruco_draw_active.setter
    def aruco_draw_active(self, value: bool):
        if not isinstance(value, bool):
            logging.warning(f'{value} is of type {type(value)}. Only boolean values are allowed for "aruco.draw_active" setting.')
        else:
            self._general_pre_proc_setter({"aruco": {"draw_active": value}})

    @property
    def aruco_draw_rgb(self) -> tuple[int, int, int]:
        """
        Black and white setting of the camera stream.

        """
        return self._general_pre_proc_getter().aruco.draw_rgb

    @aruco_draw_rgb.setter
    def aruco_draw_rgb(self, value: tuple[int, int, int]):
        if not isinstance(value, tuple | list):
            logging.warning(f'{value} is of type {type(value)}. Only list and tuple values are allowed for "aruco.draw_rgb" setting.')
            return

        for val in value:
            if not isinstance(val, int):
                logging.warning(
                    f'{value} is of type {type(value)}. Only integer values are allowed inside the tuple for the "aruco.draw_rgb" setting.'
                )
                return
        else:
            self._general_pre_proc_setter({"aruco": {"draw_rgb": value}})

    @property
    def aruco_para_set(self) -> ArucoParaSet:
        """
        Black and white setting of the camera stream.

        """
        return self._general_pre_proc_getter().aruco.para_set

    @aruco_para_set.setter
    def aruco_para_set(self, value: ArucoParaSet):
        if not isinstance(value, ArucoParaSet):
            logging.warning(f'{value} is of type {type(value)}. Only ArucoParaSet values are allowed for "aruco.draw_active" setting.')
        else:
            self._general_pre_proc_setter({"aruco": {"para_set": value}})
