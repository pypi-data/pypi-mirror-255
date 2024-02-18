import copy
import logging

import cv2 as cv
import numpy as np

from camera_management.dataclasses.aruco_dataclasses import ArucoData, ArucoParaSet, ArucoSettings


# ====================================================================================================================================================
def get_para_set(enum_entry: ArucoParaSet, print_para: bool = False) -> cv.aruco_DetectorParameters:
    """Contains aruco parameter sets which can be imported to be used for OpenCV aruco detection.

    Add other detailed aruco parameter sets inside this method.
    """
    match enum_entry:
        case ArucoParaSet.DEFAULT:
            aruco_para = cv.aruco.DetectorParameters()
        case ArucoParaSet.LARGE_DIST:
            aruco_para = cv.aruco.DetectorParameters()
            aruco_para.adaptiveThreshConstant = 11
            aruco_para.minMarkerPerimeterRate = 0.008
            aruco_para.maxMarkerPerimeterRate = 0.6
            aruco_para.polygonalApproxAccuracyRate = 0.1
            aruco_para.minCornerDistanceRate = 0.005
            aruco_para.minMarkerDistanceRate = 0.01
            aruco_para.perspectiveRemoveIgnoredMarginPerCell = 0.15
        case ArucoParaSet.MEDIUM_DIST:
            aruco_para = cv.aruco.DetectorParameters()
            # -----------------------------------------------------------------------https://amroamroamro.github.io/mexopencv/matlab/cv.detectMarkers.html
            # --------------------------------http://man.hubwiz.com/docset/OpenCV.docset/Contents/Resources/Documents/d5/dae/tutorial_aruco_detection.html
            aruco_para.adaptiveThreshWinSizeMin = (
                7  # 100                       # minimum window size for adaptive thresholding before finding contours (default 3).
            )
            # -------------------------------------------------------------------------------------------------------
            aruco_para.adaptiveThreshWinSizeMax = 27  # maximum window size for adaptive thresholding before finding contours (default 23).
            # -------------------------------------------------------------------------------------------------------
            aruco_para.adaptiveThreshWinSizeStep = (
                5  # increments from adaptiveThreshWinSizeMin to adaptiveThreshWinSizeMax during the thresholding (default 10).
            )
            # -------------------------------------------------------------------------------------------------------
            aruco_para.adaptiveThreshConstant = 20  # constant for adaptive thresholding before finding contours (default 7)
            # -------------------------------------------------------------------------------------------------------
            aruco_para.minMarkerPerimeterRate = 0.030  # determine minimum perimeter for marker contour to be detected.
            # This is defined as a rate respect to the maximum dimension
            #  of the input image (default 0.03).
            # -------------------------------------------------------------------------------------------------------
            aruco_para.maxMarkerPerimeterRate = 0.400  # determine maximum perimeter for marker contour to be detected.
            # This is defined as a rate respect to the maximum dimension of the input image (default 4.0).
            # -------------------------------------------------------------------------------------------------------
            aruco_para.polygonalApproxAccuracyRate = 0.05  # 0.05                # minimum accuracy during the polygonal approximation process to
            # determine which contours are squares. (default 0.03)
            # -------------------------------------------------------------------------------------------------------
            aruco_para.minCornerDistanceRate = 0.05  # minimum distance between corners for detected markers relative to its perimeter (default 0.05)
            # ------------------------------------------------------------------------------------------------------
            aruco_para.minDistanceToBorder = 3  # minimum distance of any corner to the image border for detected
            # markers (in pixels) (default 3)
            # ------------------------------------------------------------------------------------------------------
            aruco_para.minMarkerDistanceRate = 0.005  # minimum mean distance between two marker corners to be
            # considered similar, so that the smaller one is removed.
            # The rate is relative to the smaller perimeter of the two markers (default 0.05).
            # -------------------------------------------------------------------------------------------------------
            aruco_para.cornerRefinementMethod = 2  # cv.aruco.CORNER_REFINE_SUBPIX   #default CORNER_REFINE_NONE. 0:CORNER_REFINE_NONE, no refinement.
            # 1: CORNER_REFINE_SUBPIX, do subpixel refinement.
            # 2: CORNER_REFINE_CONTOUR use contour-Points,
            # 3: CORNER_REFINE_APRILTAG use the AprilTag2 approach).
            # -------------------------------------------------------------------------------------------------------
            aruco_para.cornerRefinementWinSize = 10  # window size for the corner refinement process (in pixels) (default 5).
            # -------------------------------------------------------------------------------------------------------
            aruco_para.cornerRefinementMaxIterations = (
                30  # maximum number of iterations for stop criteria of the corner refinement process (default 30).
            )
            # -------------------------------------------------------------------------------------------------------
            aruco_para.cornerRefinementMinAccuracy = 0.1  # minimum error for the stop criteria of the corner refinement process (default: 0.1)
            # -------------------------------------------------------------------------------------------------------
            aruco_para.markerBorderBits = 1  # number of bits of the marker border, i.e. marker border width (default 1)
            # -------------------------------------------------------------------------------------------------------
            aruco_para.perspectiveRemovePixelPerCell = (
                8  # number of bits (per dimension) for each cell of the marker when removing the perspective (default 4).
            )
            # -------------------------------------------------------------------------------------------------------
            aruco_para.perspectiveRemoveIgnoredMarginPerCell = 0.13  # width of the margin of pixels on each cell not considered for the
            # determination of the cell bit.
            # Represents the rate respect to the total size of the cell,
            # i.e. perspectiveRemovePixelPerCell (default 0.13)
            # -------------------------------------------------------------------------------------------------------
            aruco_para.maxErroneousBitsInBorderRate = 0.04  # maximum number of accepted erroneous bits in the border
            # (i.e. number of allowed white bits in the border). Represented as
            # a rate respect to the total number of bits per marker (default 0.35).
            # -------------------------------------------------------------------------------------------------------
            aruco_para.minOtsuStdDev = 1.5  # minimum standard deviation in pixels values during the decoding step
            # to apply Otsu thresholding
            # (otherwise, all the bits are set to 0 or 1 depending on mean higher
            # than 128 or not) (default 5.0)
            # -------------------------------------------------------------------------------------------------------
            aruco_para.errorCorrectionRate = 0.1  # error correction rate respect to the maximum error correction
            # capability for each dictionary (default 0.6).
            # -------------------------------------------------------------------------------------------------------
        case _:
            raise ValueError("Unknown aruco parameter set enum entry passed. Abort")

    # ------------------------------------------------------------------------------------------------------------------------------ optional printing
    if print_para:
        attributes = [attr for attr in dir(aruco_para) if not attr.startswith("__") and attr != "create"]
        print(f'Aruco detection parameters of parameter set "{enum_entry.name}:')
        for attr_str in attributes:
            attr = getattr(aruco_para, attr_str)
            print(f"\t{attr_str}:\t{attr}")

    return aruco_para


# ====================================================================================================================================================
# noinspection SpellCheckingInspection
class ArucoDetector:
    """
    initialize aruco library and parameters

    parameter:
        -> aruco_dict_name    default: 'DICT_4X4_250'
        -> aruco_para         default:  ArucoParaSet.DEFAULT
    """

    def __init__(self, settings: ArucoSettings):
        #
        self.aruco_dict = settings.dict_name
        self.aruco_para = settings.para_set
        self.active = settings.active
        self.draw_arucos = settings.draw_active
        self.draw_list: list[int] | None = None
        self.draw_rgb: tuple[int, int, int] = settings.draw_rgb

        if len(self.draw_rgb) == 3 and all(map(lambda c: isinstance(c, int), self.draw_rgb)):
            self._bgr_color = self.draw_rgb[::-1]
        else:
            logging.warning(f"Values {self.draw_rgb} could not be interpreted as BGR Color. BGR Colors must be 3 integer values up to 255.")
            self._bgr_color = (0, 0, 255)  # backup plan, red color

    @property
    def aruco_dict(self) -> cv.aruco_Dictionary:
        """
        INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        """
        return self._aruco_dict

    @aruco_dict.setter
    def aruco_dict(self, new_name: str):
        if isinstance(new_name, str):
            self._aruco_dict: cv.aruco_Dictionary = self._get_detection_dict(new_name)
        else:
            raise TypeError(f'{new_name} is of type "{type(new_name)}". Expected type "str".')

    @property
    def aruco_para(self) -> cv.aruco_DetectorParameters:
        """
        INSERT USEFUL DESCRIPTION WHEN SEEING THIS
        """
        return self._aruco_para

    @aruco_para.setter
    def aruco_para(self, new_set: ArucoParaSet):
        if not isinstance(new_set, ArucoParaSet) and not isinstance(new_set, int):
            raise TypeError(f"Expected type ArucoParaSet or int, got type {type(new_set)}.")
        if isinstance(new_set, int):
            new_set = ArucoParaSet(new_set)
        self._aruco_para = get_para_set(new_set)

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _get_detection_dict(dict_str: str) -> cv.aruco_Dictionary:
        """
        load
        """
        error = False
        if not dict_str.isupper():
            logging.warning(
                f'Input correction recommended: String for aruco dict "{dict_str}" isn\'t ' f'all uppercase as expected ("DICT_<i>X<i>_<size>").',
                stacklevel=2,
            )
        ds = dict_str.upper()
        parts = ds.split("_")
        if len(parts) == 3:
            has_prefix = parts[0] == "DICT"
            mp = parts[1].split("X")
            bit_match = len(mp) == 2 and mp[0].isnumeric() and mp[0] == mp[1]
            has_dict_size = parts[2].isnumeric()
            if not (has_prefix and bit_match and has_dict_size):
                error = True
        else:
            error = True
        if error:
            raise AttributeError(f'String for aruco dict "{dict_str}" doesn\'t match the required pattern "DICT_<i>X<i>_<size>" (case sensitive).')
        key = getattr(cv.aruco, ds)
        aruco_dict = cv.aruco.getPredefinedDictionary(key)

        return aruco_dict

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def detect_markers(self, img: np.ndarray) -> tuple[ArucoData, np.ndarray | None]:
        """Detects aruco markers visible in the returned image.

        Subpixel refinement and drawing of markers is optional.

        Output dictionary has keys... \n
        "_meta":
            "_marker_type": str, \n
            "_detected_ids": List[int], \n
            "_rejected_bboxs": Tuple[np.ndarray(1,4,2)] \n
        "data":
            "<marker_id>" one for each detected marker id, with subkeys
                "center_pt": [<pixel_x>, <pixel_y>] and \n
                "bbox_pt_1" to "bbox_pt_4" (same value format) \n
                "bbox_array": complete array of marker bbox.

        :param draw_markers: If True, draws all detected marker bounding boxes and ids into input image; only certain ids if id list is passed; no drawing if False. Default: False.
        :param draw_img: colored image for the visualisation of the measured results
        :param gray_img: grayscale image which is subject for aruco detection.
        :param rgb_color: RGB-color tuple define the border color if markers are drawn in image. Default: (0, 255, 0) (RED)
        :return: Dictionary with aruco marker data of the image as explained above, None if no aruco markers detected.
        """

        gray_img = copy.copy(img)
        # --------------------------------------------------------------------------------------- convert bgr to to gray_img
        if len(img.shape) == 3:
            gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # --------------------------------------------------------------------------------------------------------------

        bboxs, ids, rej_bboxs = cv.aruco.detectMarkers(gray_img, self._aruco_dict, parameters=self._aruco_para)
        ret_img = None

        if isinstance(ids, np.ndarray) and ids.size > 0:  # ids should be a simple list of aruco ids
            ids = ids.flatten()
            marker = ArucoData(detectedIDs=ids.tolist(), rejected_bboxs=rej_bboxs, values={})
            for idx, ar_id in enumerate(ids.tolist()):
                ar_bbox = bboxs[idx][0]
                # store point data of all aruco markers detected in the image
                cntr_pt = [
                    (ar_bbox[0][0] + ar_bbox[1][0] + ar_bbox[2][0] + ar_bbox[3][0]) / 4,
                    (ar_bbox[0][1] + ar_bbox[1][1] + ar_bbox[2][1] + ar_bbox[3][1]) / 4,
                ]
                marker.values.update(
                    {
                        str(ar_id): {
                            "center_pt": cntr_pt,
                            "bbox_array": ar_bbox,
                            "bbox_pt_1": ar_bbox[0],
                            "bbox_pt_2": ar_bbox[1],
                            "bbox_pt_3": ar_bbox[2],
                            "bbox_pt_4": ar_bbox[3],
                        }
                    }
                )
            if self.draw_arucos:
                ret_img = copy.copy(img)
                if self.draw_list is not None:
                    surplus_idx = [idx for idx, ar_id in enumerate(list(ids)) if ar_id not in self.draw_list]
                    ids = np.delete(ids, surplus_idx)
                    bboxs = np.delete(bboxs, surplus_idx, axis=0)
                cv.aruco.drawDetectedMarkers(ret_img, bboxs, ids, self._bgr_color)
        else:
            marker = ArucoData(detectedIDs=[], rejected_bboxs=rej_bboxs, values={})

        return marker, ret_img

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def marker_dict_to_numpy_arrays(
        marker_dict: dict, incl_id_list: list[int] | np.ndarray = None
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Converts specified aruco ids and a marker dict into synced arrays of aruco ids and aruco center points.
        (Optional) Passed aruco ids not in the marker dict will be skipped.

        imput:
        - marker_dict:      formatted data input with ["center_pt"] marker center points for each aruco id.
        - incl_id_list:     (optional) all aruco ids whose points should be included in the returned arrays.
                                        If None or empty, all ids are considered. Default: None.
        return:
        - np.ndarray with the available input aruco ids (shape n,)
        - np.ndarray (shape n,2) of the corresponding center points (x, y)
        """

        incl_id_list = list(map(str, incl_id_list)) if isinstance(incl_id_list, (list, np.ndarray)) else None  # str conversion for all ids in list
        include_id_array = []
        include_point_array = []
        exclude_id_array = []
        exclude_point_array = []
        for m_key, m_val in marker_dict["data"].items():
            if incl_id_list and m_key not in incl_id_list:
                # ----------------------------------------------------------------------------------------------------------- exclude
                try:
                    if (
                        isinstance(m_val["center_pt"], list)
                        and len(m_val["center_pt"]) == 2
                        and all(map(lambda f: isinstance(f, float), m_val["center_pt"]))
                    ):
                        exclude_point_array.append(m_val["center_pt"])
                    else:
                        raise TypeError('"center_pt" value for an id in marker dict is expected be a list of exactly 2 floats.')
                except KeyError as k:
                    raise KeyError(f"Aruco marker dictionary does not have the expected structure for aruco id {m_key}.") from k
                exclude_id_array.append(m_key)
            else:
                # ----------------------------------------------------------------------------------------------------------- include
                try:
                    if (
                        isinstance(m_val["center_pt"], list)
                        and len(m_val["center_pt"]) == 2
                        and all(map(lambda f: isinstance(f, float), m_val["center_pt"]))
                    ):
                        include_point_array.append(m_val["center_pt"])
                    else:
                        raise TypeError('"center_pt" value for an id in marker dict is expected be a list of exactly 2 floats.')
                except KeyError as k:
                    raise KeyError(f"Aruco marker dictionary does not have the expected structure for aruco id {m_key}.") from k
                include_id_array.append(m_key)

        include_id_array = np.array(include_id_array, int)
        include_point_array = np.array(include_point_array, np.float32)

        exclude_id_array = np.array(exclude_id_array, int)
        exclude_point_array = np.array(exclude_point_array, np.float32)

        return include_id_array, include_point_array, exclude_id_array, exclude_point_array
