from enum import IntEnum

import pydantic_numpy.typing as pnd
from pydantic import BaseModel, field_validator


class ArucoParaSet(IntEnum):
    """
    presets for aruco parameter
    """

    DEFAULT = 1
    LARGE_DIST = 2
    MEDIUM_DIST = 3


class ArucoSettings(BaseModel):
    dict_name: str = "DICT_4X4_1000"
    para_set: ArucoParaSet = ArucoParaSet.DEFAULT
    active: bool = False
    draw_active: bool = False
    draw_rgb: tuple[int, int, int] = (0, 255, 0)

    @field_validator("draw_rgb")
    def list_to_tuple(cls, draw_rgb) -> tuple[int, int, int]:
        """
        Validator for draw_rgb setting.
        """
        if isinstance(draw_rgb, tuple) or isinstance(draw_rgb, list):
            draw_rgb = tuple(draw_rgb)
            if len(draw_rgb) != 3:
                raise AttributeError(f"There were {len(draw_rgb)} values supplied. Please supply a list or tuple of 3 RGB (0-255) integer values.")
            else:
                for val in draw_rgb:
                    if not isinstance(val, int):
                        raise AttributeError(f"Value {val} is of type {type(val)}. Please supply a list or tuple of 3 RGB (0-255) integer values.")
            return draw_rgb

        else:
            raise AttributeError(f"Value {draw_rgb} is of type {type(draw_rgb)}. Please supply a list or tuple of 3 RGB (0-255) integer values.")

    @field_validator("dict_name")
    def name_must_be(cls, dict_name) -> str:
        """
        Validator for dict_name setting.
        """
        error = False
        ds = dict_name.upper()
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
            raise AttributeError(f'String for aruco dict "{dict_name}" doesn\'t match the required pattern "DICT_<i>X<i>_<size>" (case sensitive).')
        else:
            return dict_name


class ArucoData(BaseModel):
    detectedIDs: list
    rejected_bboxs: pnd.NpNDArray | None
    values: dict
