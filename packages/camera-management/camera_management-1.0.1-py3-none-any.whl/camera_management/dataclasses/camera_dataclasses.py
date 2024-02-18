from __future__ import annotations

from typing import Any, Literal

import cv2 as cv
import numpy as np
from pydantic import BaseModel, field_validator

from camera_management.dataclasses.general_dataclasses import ImageResolution, VideoDevice
from camera_management.measurement_operators.aruco_detection import ArucoSettings


class PreprocessingSettings(BaseModel):
    bw: bool = False
    undistort: bool = False
    rotate: int = 0
    aruco: ArucoSettings

    @field_validator("rotate")
    def rotate_must_be_in(cls, rotate):
        """
        Validator for rotation setting.
        """
        allowed_values = [0, 90, 180, 270]
        if rotate not in allowed_values:
            raise ValueError(f"Rotation value of {rotate} is not valid. Only rotate values of {allowed_values} are allowed.")
        return rotate


class InnerCoeff(BaseModel):
    fx: float | None = None
    fy: float | None = None
    cx: float | None = None
    cy: float | None = None
    fx_std: float = float(0.0)
    fy_std: float = float(0.0)
    cx_std: float = float(0.0)
    cy_std: float = float(0.0)

    def model_post_init(self, __context: Any) -> None:
        """
        Generates the camera matrix after all values have been initialized.
        """
        self._generate_camera_matrix()

    def get_from_resolution(self, res: ImageResolution) -> InnerCoeff:
        """
        A set of inner camera matrix - coefficients (fx, fy, cx, cy) for a specific image stream_resolution (ImageResolution -> x, y) with the defaults:
         - stream_resolution 1280 x 720 Pixel
         - fx = fy = 1280 Pixel
         - cx = 640 Pixel
         - cy = 360 Pixel

        => CAUTION: stream_resolution changes require scaling of the coefficients!

        Help: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
        """
        self.fx: float = float(res.x)
        self.fy: float = float(res.x)
        self.cx: float = float(res.x / 2)
        self.cy: float = float(res.y / 2)

        self.fx_std: float = float(0.0)
        self.fy_std: float = float(0.0)
        self.cx_std: float = float(0.0)
        self.cy_std: float = float(0.0)

        return self

    def __str__(self) -> str:
        coeff_string = "inner camera coefficients:\t" + f"fx: {self._fx} |\t" + f"fy: {self._fy} |\t" + f"cx: {self._cx} |\t" + f"cy: {self._cy}"
        return coeff_string

    @property
    def get_camera_matrix(self) -> np.array:
        """Gets the CV camera matrix as an np.ndarray.

        :return: _cam_matrix = ndarray[ [fx, 0, cx], [0, fy, cy], [0, 0, 1] ]
        """

        return self._cam_matrix

    @property
    def get_camera_parameter(self) -> np.array:
        """Gets the CV camera matrix as an np.ndarray.

        :return: ndarray[ fx, std_fx, fy, std_fy, cx, std_cx,  cy, std_cy]]
        """

        return np.array(
            (self._fx, self._fx_std, self._fy, self._fy_std, self._cx, self._cx_std, self._cy, self._cy_std),
            dtype=float,
        )

    def _generate_camera_matrix(self):
        """
        generates the camera matrix from the inner coefficients
        """
        self._cam_matrix = np.array([[self.fx, 0, self.cx], [0, self.fy, self.cy], [0, 0, 1]], dtype=np.float32)

    def set_inner_coeff(
        self,
        fx: float | None = None,
        fy: float | None = None,
        cx: float | None = None,
        cy: float | None = None,
        calibration_resolution: ImageResolution | None = None,
    ):
        """
        Sets inner camera coefficient values with one method call.
        -> fx, fy, cx, cy and calibration_resolution
        -> if a parameter is None it will be skipped.

        CAUTION: stream_resolution changes require scaling of the coefficients!
        """

        if calibration_resolution is not None:
            self.calibration_resolution = calibration_resolution

        if fx is not None:
            self._fx = fx

        if fy is not None:
            self._fy = fy

        if cx is not None:
            self._cx = cx

        if cy is not None:
            self._cy = cy

        self._generate_camera_matrix()

    def set_inner_coeff_stds(
        self,
        fx: float | None = None,
        fy: float | None = None,
        cx: float | None = None,
        cy: float | None = None,
    ):
        """Sets multiple inner camera coefficient _values_ with one method call.

        Parameters: _fx, _fy, _cx, _cy - if one is None (Default) parameter will be skipped.
        """
        if fx is not None:
            self._fx_std = fx
        if fy is not None:
            self._fy_std = fy
        if cx is not None:
            self._cx_std = cx
        if cy is not None:
            self._cy_std = cy

    def scale_inner_coeff(self, target_resolution: ImageResolution):
        """
        Uses a scaling factor to adapt the inner coefficients to other resolutions than the original stream_resolution on instantiation.
        Overwrites instance variables (including stds).
        :param
            target_resolution: ImageResolution -> scale the inner coefficients  to this actual_resolution
        """

        scale_factor_x = target_resolution.x / self.calibration_resolution.x
        scale_factor_y = target_resolution.y / self.calibration_resolution.y

        self.set_inner_coeff(scale_factor_x * self._fx, scale_factor_y * self._fy, scale_factor_x * self._cx, scale_factor_y * self._cy)
        self.set_inner_coeff_stds(
            scale_factor_x * self._fx_std,
            scale_factor_y * self._fy_std,
            scale_factor_x * self._cx_std,
            scale_factor_y * self._cy_std,
        )

    def to_dict(self, build_in_types=True) -> dict:
        """
        Helper function to get the core content as dict.
        """
        output = {
            "fx": self._fx,
            "fy": self._fy,
            "cx": self._cx,
            "cy": self._cy,
            "fx_std": self._fx_std,
            "fy_std": self._fy_std,
            "cx_std": self._cx_std,
            "cy_std": self._cy_std,
            "calibration_resolution_x": self.calibration_resolution.x,
            "calibration_resolution_y": self.calibration_resolution.y,
            "calibration_resolution_channels": self.calibration_resolution.channels,
        }
        if build_in_types:
            for k, v in output.items():
                output[k] = float(v)

        return output


# ================================================================================================================================== class = DistCoeff
class DistCoeff(BaseModel):
    """
    A complete set (np.ndarray(14,1) of opencv distortion coefficients (k1, k2, p1, p2, k3, k4, k5, k6, s1, s2, s3, s4, t1, t2) with default 0.0
    """

    k1: float = 0.0
    k2: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    k3: float = 0.0
    k4: float = 0.0
    k5: float = 0.0
    k6: float = 0.0
    s1: float = 0.0
    s2: float = 0.0
    s3: float = 0.0
    s4: float = 0.0
    t1: float = 0.0
    t2: float = 0.0
    k1_std: float = 0.0
    k2_std: float = 0.0
    p1_std: float = 0.0
    p2_std: float = 0.0
    k3_std: float = 0.0
    k4_std: float = 0.0
    k5_std: float = 0.0
    k6_std: float = 0.0
    s1_std: float = 0.0
    s2_std: float = 0.0
    s3_std: float = 0.0
    s4_std: float = 0.0
    t1_std: float = 0.0
    t2_std: float = 0.0

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    @property
    def get_dist_coeff_values(self) -> np.ndarray:
        """Returns the values of the distortion coefficient as an np.ndarray.

        :return: coeff_values = ndarray[k1, k2, p1, p2, k3, k4, k5, k6, s1, s2, s3, s4, t1, t2]
        """
        coeff_values = np.array(
            [
                self.k1,
                self.k2,
                self.p1,
                self.p2,
                self.k3,
                self.k4,
                self.k5,
                self.k6,
                self.s1,
                self.s2,
                self.s3,
                self.s4,
                self.t1,
                self.t2,
            ],
            dtype=np.float32,
        )

        return coeff_values

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def set_dist_coeff_values(
        self,
        k1=None,
        k2=None,
        p1=None,
        p2=None,
        k3=None,
        k4=None,
        k5=None,
        k6=None,
        s1=None,
        s2=None,
        s3=None,
        s4=None,
        t1=None,
        t2=None,
    ):
        """Sets multiple distortion coefficient _values_ with one method call.

        Parameters: k1, k2, p1, p2, k3-k6, s1-s4, t1, t2 - if one is None (Default) parameter will be skipped.
        """
        if k1 is not None:
            self.k1 = k1
        if k2 is not None:
            self.k2 = k2
        if p1 is not None:
            self.p1 = p1
        if p2 is not None:
            self.p2 = p2
        if k3 is not None:
            self.k3 = k3
        if k4 is not None:
            self.k4 = k4
        if k5 is not None:
            self.k5 = k5
        if k6 is not None:
            self.k6 = k6
        if s1 is not None:
            self.s1 = s1
        if s2 is not None:
            self.s2 = s2
        if s3 is not None:
            self.s3 = s3
        if s4 is not None:
            self.s4 = s4
        if t1 is not None:
            self.t1 = t1
        if t2 is not None:
            self.t2 = t2

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def set_dist_coeff_stds(
        self,
        k1=None,
        k2=None,
        p1=None,
        p2=None,
        k3=None,
        k4=None,
        k5=None,
        k6=None,
        s1=None,
        s2=None,
        s3=None,
        s4=None,
        t1=None,
        t2=None,
    ):
        """Sets multiple distortion coefficient _standard deviations_ with one method call.

        Parameters: k1, k2, p1, p2, k3-k6, s1-s4, t1, t2 - if one is None (Default) parameter will be skipped.
        """
        if k1 is not None:
            self.k1_std = k1
        if k2 is not None:
            self.k2_std = k2
        if p1 is not None:
            self.p1_std = p1
        if p2 is not None:
            self.p2_std = p2
        if k3 is not None:
            self.k3_std = k3
        if k4 is not None:
            self.k4_std = k4
        if k5 is not None:
            self.k5_std = k5
        if k6 is not None:
            self.k6_std = k6
        if s1 is not None:
            self.s1_std = s1
        if s2 is not None:
            self.s2_std = s2
        if s3 is not None:
            self.s3_std = s3
        if s4 is not None:
            self.s4_std = s4
        if t1 is not None:
            self.t1_std = t1
        if t2 is not None:
            self.t2_std = t2

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        coeff_string = (
            "distortion coefficients:\t"
            + f"k1: {self.k1} |\tk2: {self.k2} |\t"
            + f"p1: {self.p1} |\tp2: {self.p2} |\t"
            + f"k3: {self.k3} |\tk4: {self.k4} |\tk5: {self.k5} |\tk6: {self.k6} |\t"
            + f"s1: {self.s1} |\ts2: {self.s2} |\ts3: {self.s3} |\ts4: {self.s4} |\t"
            + f"t1: {self.t1} |\tt2: {self.t2}"
        )
        return coeff_string


class ExtrinsicPara:
    """
    extrinsic orientation of a camera -> TODO: Pose_Trafo
    """

    def __init__(
        self,
        x: np.float32 = 0.0,
        y: np.float32 = 0.0,
        z: np.float32 = 0.0,
        rx: np.float32 = 0.0,
        ry: np.float32 = 0.0,
        rz: np.float32 = 0.0,
        x_std: np.float32 = 0.0,
        y_std: np.float32 = 0.0,
        z_std: np.float32 = 0.0,
        rx_std: np.float32 = 0.0,
        ry_std: np.float32 = 0.0,
        rz_std: np.float32 = 0.0,
    ):
        self.x = np.float32(x)
        self.y = np.float32(y)
        self.z = np.float32(z)
        self.rx = np.float32(rx)
        self.ry = np.float32(ry)
        self.rz = np.float32(rz)

        self.x_std = np.float32(x_std)
        self.y_std = np.float32(y_std)
        self.z_std = np.float32(z_std)
        self.rx_std = np.float32(rx_std)
        self.ry_std = np.float32(ry_std)
        self.rz_std = np.float32(rz_std)

    def get_array(self) -> np.ndarray:
        """
        INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        """
        return np.array([self.x, self.y, self.z, self.rx, self.ry, self.rz], dtype=np.float32)

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        extrinsic_string = (
            "extrinsic parameter:\t"
            + f"x: {self.x} |\t"
            + f"y: {self.y} |\t"
            + f"z: {self.z} |\t"
            + f"rx: {self.z} |\t"
            + f"ry: {self.z} |\t"
            + f"rz: {self.z} |\t"
        )
        return extrinsic_string

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    @property
    def extrinsic_vector(self) -> np.ndarray:
        """
        INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        """
        return np.array([self.x, self.y, self.z, self.rx, self.ry, self.rz], dtype=np.float32)

    @extrinsic_vector.setter
    def extrinsic_vector(self, new_vector: list[np.float32] | np.ndarray):
        array_condition = isinstance(new_vector, np.ndarray) and new_vector.shape == (6,)
        list_condition = all(map(lambda e: isinstance(e, np.float32), new_vector))
        if array_condition or list_condition:
            self.x = new_vector[0]
            self.y = new_vector[1]
            self.z = new_vector[2]
            self.rx = new_vector[3]
            self.ry = new_vector[4]
            self.rz = new_vector[5]

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    @property
    def extrinsic_std_vector(self) -> np.array:
        """
        INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        """
        return np.array([self.x_std, self.y_std, self.z_std, self.rx_std, self.ry_std, self.rz_std], np.float32)

    @extrinsic_std_vector.setter
    def extrinsic_std_vector(self, new_vector: list[np.float32] | np.ndarray):
        array_condition = isinstance(new_vector, np.ndarray) and new_vector.shape == (6,)
        list_condition = all(map(lambda e: isinstance(e, np.float32), new_vector))
        if array_condition or list_condition:
            self.x_std = new_vector[0]
            self.y_std = new_vector[1]
            self.z_std = new_vector[2]
            self.rx_std = new_vector[3]
            self.ry_std = new_vector[4]
            self.rz_std = new_vector[5]


class BrownCameraDescr(BaseModel):
    """
    TODO: Vollständig ausformulieren
    """

    c: float = 0.0
    x0: float = 0.0
    y0: float = 0.0
    r0: float = 0.0
    a1: float = 0.0
    a2: float = 0.0
    a3: float = 0.0
    b1: float = 0.0
    b2: float = 0.0


class CameraCalibrationData(BaseModel):
    mode: Literal["type", "individual"]
    available: bool
    values: CalibrationValuesOpenCV | None  # CalibrationValuesBrown (sometime in the future this will also be a model)
    model: Literal["OpenCV_standard", "brown"] | None


class CameraInformation(BaseModel):
    standard_resolution: ImageResolution
    available_resolutions: list[ImageResolution]
    device: VideoDevice
    resolution_roi_coupled: bool


class CameraDebug(BaseModel):
    last_updated: str
    created_on_platform: str


class CalibrationValuesOpenCV(BaseModel):
    calibration_resolution: ImageResolution
    intrinsic_values: InnerCoeff
    distortion_coefficients: DistCoeff

    def model_post_init(self, __context: Any) -> None:
        """
        Sets the intrinsic values based on the calibration resolution if there are no intrinsic values given.
        """
        if self.intrinsic_values.cy and self.intrinsic_values.cx and self.intrinsic_values.fx and self.intrinsic_values.fy is None:
            self.intrinsic_values.get_from_resolution(self.calibration_resolution)

    def get_brown_para(self) -> BrownCameraDescr:
        """
        Converts OpenCV camera parameters to brwon camera parameters (standard photogrammetric camera model)
        TODO: add complete parameter set
        """
        def_pix_size = 1  # 1 mm/Pixel
        f = 0.5 * (self.intrinsic_values.fx + self.intrinsic_values.fy) * def_pix_size  # [mm] auf virtuellem Sensor

        descr = BrownCameraDescr()
        # --------------------------------------------------------------------------------------------
        descr.r0 = (
            2 / 3 * np.sqrt((0.5 * self.calibration_resolution.x * def_pix_size) ** 2 + (0.5 * self.calibration_resolution.y * def_pix_size) ** 2)
        )
        # --------------------------------------------------------------------------------------------
        descr.c = -f
        descr.x0 = self.intrinsic_values.cx * def_pix_size - 0.5 * self.calibration_resolution.x * def_pix_size
        descr.y0 = -self.intrinsic_values.cy * def_pix_size + 0.5 * self.calibration_resolution.y * def_pix_size
        # --------------------------------------------------------------------------------------------
        descr.a1 = self.distortion_coefficients.k1 / f**2
        descr.a2 = self.distortion_coefficients.k2 / f**4
        descr.a3 = self.distortion_coefficients.k3 / f**6

        descr.b1 = self.distortion_coefficients.p2 / f**2
        descr.b2 = -self.distortion_coefficients.p1 / f**2

        return descr


class CameraDescription(BaseModel):
    information: CameraInformation
    calibration: CameraCalibrationData
    config: dict = {}
    debug: CameraDebug


def get_undistort_image(img, mtx, dist, crop_image: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """Function to undistort the image. Calculates new camera matrix (after cropping or for undistortion).
    :param img: image (distorted, undistort)
    :param mtx: camera matrix from json-file
    :param dist: distortion_coefficients from json file
    :param crop_image: if True, do cropping
    :return: cropped image, new camera matrix
    -> https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html
    """
    # -> https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html#ga7dfb72c9cf9780a347fbe3d1c47e5d5a
    # Refining the camera matrix using parameters obtained by calibration
    # mtx = np.array([[innerPara[0], 0, innerPara[2]], [0, innerPara[1], innerPara[3]], [0, 0, 1]]) --> wenn aus json Datei gelesen wird
    # mtx = np.array([[innerPara[0][0], 0, innerPara[0][2]], [0, innerPara[0][1], innerPara[0][3]], [0, 0, 1]])
    # TODO: handle gray images in the same way!

    # ------------------------------------------------------------------------------------------------------------------------------------- image size
    h, w = img.shape[:2]
    # ------------------------------------------------------------------------------------------- Query whether new_camera_matrix should be determined
    if crop_image:
        new_cam_matrix, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    else:
        roi = 0, 0, w, h
        new_cam_matrix = mtx
    # ----------------------------------------------------------------------------------Computes the undistortion and rectification transformation map
    mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, new_cam_matrix, (w, h), 5)  # 5=CV_32FC1, 11=CV_16SC2, 13=CV_32FC2
    undistort_img = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
    # --------------------------------------------------------------------------------------------------------------------------------- crop the image
    x, y, w, h = roi
    undistort_img = undistort_img[y : y + h, x : x + w]
    # ------------------------------------------------------------------------------------------------------------------------- new mtx after cropping
    # https://docs.opencv.org/3.4/d9/d0c/group__calib3d.html#ga7a6c4e032c97f03ba747966e6ad862b1
    if crop_image:
        no_dist = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], float)
        h, w = undistort_img.shape[:2]
        new_cam_matrix, roi = cv.getOptimalNewCameraMatrix(new_cam_matrix, no_dist, (w, h), 1, (w, h))

    return undistort_img, new_cam_matrix
