import threading
import time
import uuid
from queue import Queue

import cv2 as cv

from camera_management.dataclasses.camera_dataclasses import ArucoSettings, CameraDescription, get_undistort_image
from camera_management.dataclasses.general_dataclasses import ArucoData, ImageProcessorData, MeasurementData
from camera_management.measurement_operators.aruco_detection import ArucoDetector
from camera_management.tools._camera_handler import setup_camera
from camera_management.tools._camera_thread import CameraThread


class ImageProcessor(threading.Thread):
    def __init__(
        self,
        cam_param: CameraDescription,
        stop_event: threading.Event = None,
        undistort=True,
        bw=False,
        rotate=0,
        aruco_detector: ArucoDetector = ArucoDetector(ArucoSettings()),
        *args,
        **kwargs,
    ):
        """
        base class for a thread to measure in an opencv image stream
        """
        name = f"processor_{cam_param.information.device.product}"
        self._args = args
        self._kwargs = kwargs
        self._mutex: threading.Lock = threading.Lock()
        self._last_change = 0
        self._bw = bw
        self._undistort = undistort
        self._rotate = rotate
        self._aruco_detector: ArucoDetector = aruco_detector
        self._image_data: ImageProcessorData = ImageProcessorData()
        self._meas_data: MeasurementData = MeasurementData(aruco=ArucoData(detectedIDs=[], rejected_bboxs=None, values={}))
        # self.logger = get_logger(f"tools.ip.{cam_param.custom_cam_name}")

        super().__init__(daemon=False, name=name)

        if stop_event is None:
            stop_event = threading.Event()

        self.stop_event = stop_event

        self.camera = None

        # --------------------------------------------------------------------------------------------------------------------------------------------
        self.cam_param: CameraDescription = cam_param
        self.maxsize = 1
        self._queue = Queue(maxsize=self.maxsize + 1)

    def run(self):
        """
        Runs the main function.
        """
        self._init_stream()
        self._cam_stream()

    def _init_stream(self):
        """
        INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        """
        cap, _ = setup_camera(device=self.cam_param.information.device, resolution=self.cam_param.information.standard_resolution)
        self.camera = CameraThread(cap, self.cam_param.information.device.path, autostart=True)

    def set_camera_options(self, arg: int, val):
        """
        Set a camera setting.

        :param arg: The setting to ask for encoded as an enum. Available enums are listed in the documentation.
        :param val: The value you want to set it to.
        """
        return self.camera.set_cap(arg, val)

    def get_camera_options(self, arg: int):
        """
        Get a camera setting.

        :param arg: The setting to ask for encoded as an enum. Available enums are listed in the documentation.
        """

        return self.camera.get_cap(arg)

    def stop(self):
        """
        Set stop = True, ending the running loop.
        Call OBJECT.join() afterwards, to wait for the thread to finish.
        """
        # self.logger.debug("Stopping")
        self.stop_event.set()

    def _cam_stream(self):
        """
        Main workhorse function of the class.
        """
        # ----------------------------------------------------------------------------------- init parameters for distortion and for spatial resection
        # self.logger.debug("Starting")

        if self.cam_param.calibration.available:
            cam_matrix = self.cam_param.calibration.values.intrinsic_values.get_camera_matrix
            dist_coeff = self.cam_param.calibration.values.distortion_coefficients.get_dist_coeff_values
        else:
            cam_matrix = None
            dist_coeff = None

        frame_cnt = 1
        curr_fps, avg_fps = 0, 0

        # --------------------------------------------------------------------------------------------------------------------------------------------
        while not self.stop_event.is_set():
            result = {"timestamps": [("Start", time.perf_counter())]}
            uid = uuid.uuid4()
            # ---------------------------------------------------------------------------------------------------------------------- undistort image
            frame = self.camera.get_frame()
            if frame is None:
                continue

            if self._undistort and self.cam_param.calibration.available:
                frame.data, _ = get_undistort_image(frame.data, cam_matrix, dist_coeff, False)

            if self._bw:
                frame.data = cv.cvtColor(frame.data, cv.COLOR_BGR2GRAY)
            else:
                pass

            if self._rotate == 0:
                pass
            elif self._rotate == 90:
                frame.data = cv.rotate(frame.data, cv.ROTATE_90_CLOCKWISE)
            elif self._rotate == 180:
                frame.data = cv.rotate(frame.data, cv.ROTATE_180)
            elif self._rotate == 270:
                frame.data = cv.rotate(frame.data, cv.ROTATE_90_COUNTERCLOCKWISE)

            result["timestamps"].append(("End", time.perf_counter()))
            curr_fps, avg_fps = self._calc_fps(result["timestamps"][0][1], result["timestamps"][-1][1], avg_fps, frame_cnt)
            frame_cnt += 1  # Important for avg_fps calculation!

            if self._aruco_detector.active:
                markers, res_image = self._aruco_detector.detect_markers(frame.data)
                self._meas_data.aruco = markers
                self._meas_data.id = uid
                self._meas_data.timestamp = time.time_ns()
                if res_image is not None:
                    frame.data = res_image

            self.image_data = ImageProcessorData(time.time_ns(), frame.data, curr_fps=curr_fps, avg_fps=avg_fps, id=uid)

            # print(result["timestamps"][-1][1] - result["timestamps"][0][1])

        # self.logger.debug("Stopping camera thread..")
        # End controlled camera stream
        self.camera.stop()
        self.camera.join()
        # self.logger.debug("Stopped")

    @property
    def image_data(self):
        """
        INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        """
        locked = self._mutex.acquire(blocking=True, timeout=0.1)
        if locked:
            data = self._image_data
            self._mutex.release()
            return data

    @image_data.setter
    def image_data(self, data: ImageProcessorData):
        locked = self._mutex.acquire(blocking=True, timeout=0.1)
        if locked:
            self._image_data = data
            self._mutex.release()

    @property
    def measure_data(self):
        """
        INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        """
        locked = self._mutex.acquire(blocking=True, timeout=0.1)
        if locked:
            data = self._meas_data
            self._mutex.release()
            return data

    @measure_data.setter
    def measure_data(self, data: dict):
        locked = self._mutex.acquire(blocking=True, timeout=0.1)
        if locked:
            self._meas_data = data
            self._mutex.release()

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _calc_fps(start_time: time, end_time: time, old_avg_fps: float, cnt: int) -> tuple[float, float]:
        """Function that calculates current and average fps."""
        curr_fps = 1.0 / (end_time - start_time)
        avg_fps = (old_avg_fps * (cnt - 1) + curr_fps) / cnt

        return curr_fps, avg_fps
