import atexit
import json
import logging
import pathlib
import pickle
import threading
import time
from datetime import datetime

import cv2 as cv
import numpy as np
from flask import Flask, Response, jsonify, make_response, request
from waitress import serve

from camera_management import SETTINGS
from camera_management.dataclasses import general_dataclasses
from camera_management.dataclasses.camera_dataclasses import ArucoSettings, CameraDescription, PreprocessingSettings
from camera_management.measurement_operators.aruco_detection import ArucoDetector
from camera_management.tools._image_processor import ImageProcessor
from camera_management.tools.config_tools import check_preprocessing, write_configuration_file

logger = logging.getLogger("camera_management.camera_interface")


class CameraApplication(threading.Thread):
    """
    Handles the incoming calls to set camera/preprocessing settings and serves the camera stream.
    """

    def __init__(self, port: int):
        super().__init__(name=f"Camera Interface Port {port}")
        self.description: CameraDescription | None = None
        self.preprocessing_settings = PreprocessingSettings(bw=False, undistort=False, rotate=0, aruco=ArucoSettings())
        self._flask = Flask(__name__)
        self._port = port
        self._status = "OFFLINE"
        self._temp_path = pathlib.Path(__file__).parent / f"temp/configs/{self._port}.json"
        self._wait_for_config()
        self._preprocessing_thread = ImageProcessor(cam_param=self.description, stop_event=None)
        self._preprocessing_thread.start()
        self._last_frame = general_dataclasses.ImageProcessorData(image=np.zeros((1080, 720)))

        # @self._flask.get("/log")
        # def _get_log():
        #     """
        #     INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        #     """
        #     return jsonify(_interface.data.log_unit)

        # @self._flask.get("/info/cameras")
        # def get_camera_info():
        #     """
        #     INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        #     """
        #     return jsonify(self.cam)

        @atexit.register
        def __exit():
            self._preprocessing_thread.stop()

        @self._flask.get("/data/imageProcessor")
        def img_processor():
            """
            Flask getter for the actual image data.
            """

            data: general_dataclasses.ImageProcessorData = self._preprocessing_thread.image_data
            if data.image is None:
                data = self._last_frame
            else:
                self._last_frame = data

            response = make_response(pickle.dumps(data))
            response.headers.set("content-type", "application/octet-stream")
            response.headers.set("digest", "TODO")
            response.headers.set("last_change", f"{self._preprocessing_thread._last_change}")

            return response

        @self._flask.get("/data/processed")
        def get_processed():
            """
            Flask getter for data from image measurement operators.
            """
            data: general_dataclasses.MeasurementData = self._preprocessing_thread.measure_data
            response = make_response(pickle.dumps(data))
            response.headers.set("content-type", "application/octet-stream")
            response.headers.set("digest", "TODO")
            response.headers.set("last_change", f"{self._preprocessing_thread._last_change}")

            return response

        @self._flask.get("/status")
        def get_status():
            """
            Flask getter for the camera status.
            """
            return jsonify({"status": self._status})

        @self._flask.route("/settings/pre_processing", methods=["GET", "POST"])
        def set_pre_processing_settings():
            """
            Flask route to set and get preprocessing settings.
            """
            if request.method == "POST":
                status, self.preprocessing_settings = check_preprocessing(request.json, self.preprocessing_settings)
                if status != "SUCCESS":
                    return status, 400

                if self.preprocessing_settings.undistort and not self.description.calibration.available:
                    self.preprocessing_settings.undistort = False
                    return "Can only undistort image if there are calibration values present. All pre-processing settings were rejected.", 400

                self._preprocessing_thread.stop_event.set()
                self._preprocessing_thread.join()

                self._preprocessing_thread = ImageProcessor(
                    cam_param=self.description,
                    stop_event=None,
                    bw=self.preprocessing_settings.bw,
                    undistort=self.preprocessing_settings.undistort,
                    rotate=self.preprocessing_settings.rotate,
                    aruco_detector=ArucoDetector(self.preprocessing_settings.aruco),
                )
                self._preprocessing_thread.start()
                return jsonify(self.preprocessing_settings.model_dump())

            elif request.method == "GET":
                return jsonify(self.preprocessing_settings.model_dump())
            else:
                return f"Request with method {request.method} was not accepted.", 400

        @self._flask.get("/description")
        def get_description():
            """
            Flask getter for the camera description.
            """
            return jsonify(self.description.model_dump())

        @self._flask.route("/settings/camera", methods=["GET", "POST"])
        def camera_settings():
            """
            Receives http requests and tries to set the values received.
            """

            if request.method == "POST":
                settings = json.loads(request.data)["settings"]
                status, ret = self._preprocessing_thread.set_camera_options(settings[0], settings[1])
                if status == -1:
                    return Response(f"Error while trying to set {settings[0]}: {ret}", 400)
                self.description.config[settings[0]] = settings[1]
                self.description.debug.last_updated = datetime.today().strftime("%d-%m-%Y %H:%M:%S")
                write_configuration_file(
                    filename=f"{self._port}.json", cam_config_path=self._temp_path.parent.parent, content=self.description.model_dump()
                )

                return Response(
                    f"Tried to set {SETTINGS(settings[0]).name} to {settings[1]}. {SETTINGS(settings[0]).name} got set to {ret[settings[0]]}. "
                )
            elif request.method == "GET":
                settings = int(request.args.get("settings"))
                status, ret = self._preprocessing_thread.get_camera_options(settings)
                if status == -1:
                    return Response(f"Error while trying to get setting {SETTINGS(settings).name}: {ret}", 400)
                return jsonify({SETTINGS(settings).name: ret})
            else:
                return f"Request with method {request.method} was not accepted.", 400

        def _gen_frames():
            ret, buffer = cv.imencode(".jpg", self._preprocessing_thread.image_data.image)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")  # concat frame one by one and show result

        @self._flask.route("/video_feed")
        def video_feed():
            return Response(_gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

        #
        #
        # @self._flask.get("/kill")
        # def die_get():
        #     """
        #     INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        #     """
        #     return render_template("kill_help.html")

    def _wait_for_config(self):
        """
        If no config is found this function will wait until there is one.
        """
        already_waiting_for_config = False
        while self.description is None:
            try:
                self.description = CameraDescription.model_validate(json.load(open(self._temp_path)))
                logging.info(f"Port {self._port}: Found camera config.")
            except FileNotFoundError:
                if not already_waiting_for_config:
                    logging.warning(f"No config found in {self._temp_path}. Retrying.")
                    already_waiting_for_config = True
            time.sleep(1)

    def run(self):
        """
        Run the server.
        """
        self._status = "ONLINE"
        serve(self._flask, host="0.0.0.0", port=self._port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start a Camera Application.")
    parser.add_argument("port", metavar="p", type=int, help="port for the camera application")
    args = parser.parse_args()

    cam_app = CameraApplication(args.port)
    cam_app.start()
