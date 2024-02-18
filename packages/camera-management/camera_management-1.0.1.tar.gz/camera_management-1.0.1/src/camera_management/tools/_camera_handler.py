import logging

import cv2 as cv

from camera_management._camera_backends.basler_handler import BaslerDevice_a2A5328_15ucBAS, BaslerDevice_acA5472_17uc
from camera_management.dataclasses.general_dataclasses import ImageResolution, VideoDevice

logger = logging.getLogger("camera-management.camera_handler")
try:
    from camera_management._camera_backends.avt_handler import AVTDevice

    avt_import = True
except Exception:
    avt_import = False
    logger.warning("camera_handler: (Ignore if you do not want to use AVT Cameras) Could not import AVTDevice. See the readme for more information.")


def encode_codec(code: str):
    """
    Encode codec as fourcc as in:
    cv.CAP_PROP_FOURCC
    (https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#gaeb8dd9c89c10a5c63c139bf7c4f5704d)
    """
    if len(code) != 4:
        raise ValueError("Need 4 characters")

    return int.from_bytes(code.encode(), "little")


def decode_codec(code: int):
    """
    Decode codec as fourcc as in:
    cv.CAP_PROP_FOURCC
    (https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#gaeb8dd9c89c10a5c63c139bf7c4f5704d)
    """
    code = int(code)
    # Inverse the sequence, since we have little endian
    return bytes.fromhex(f"{code:08x}")[::-1].decode()


def configure_stream(cap: cv.VideoCapture, resolution: ImageResolution, codec: str) -> tuple[dict, cv.VideoCapture]:
    """
    INSERT USEFUL DESCRIPTION WHEN SEEING THIS
    """
    # Setting codec. When codec is wrong, it may be that the desired resolution is unachievable
    current_codec = cap.get(cv.CAP_PROP_FOURCC)
    current_codec = decode_codec(current_codec)

    if current_codec != codec:
        # _logger.info(f'Setting used coded from "{current_codec}" to "{codec}"...')
        cap.set(cv.CAP_PROP_FOURCC, encode_codec("MJPG"))

        current_codec = cap.get(cv.CAP_PROP_FOURCC)
        current_codec = decode_codec(current_codec)
        if current_codec == codec:
            pass
            # _logger.info("successful")
        else:
            error_str = f' Setting codec failed. Codec is "{current_codec}"'
            # _logger.error(error_str)
            RuntimeError(error_str)

    # Setting resolution
    # _logger.info(f"Set-Resolution: {resolution}...")
    cap.set(cv.CAP_PROP_FRAME_WIDTH, resolution.x)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, resolution.y)
    actual_resolution = ImageResolution(x=int(cap.get(cv.CAP_PROP_FRAME_WIDTH)), y=int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)), channels=3)

    if actual_resolution == resolution:
        # _logger.info("success!")
        pass
    else:
        error_str = f"Target resolution could not be set. Actual resolution is: {actual_resolution}."
        # _logger.error(error_str)
        logger.warning(error_str)

    return {"codec": current_codec, "resolution": actual_resolution}, cap


def setup_camera(device: VideoDevice, resolution: ImageResolution) -> tuple[cv.VideoCapture, ImageResolution]:
    """
    INSERT USEFUL DESCRIPTION WHEN SEEING THIS
    """
    # # _logger.info(f"Setup {device}")

    if device.product == "a2A5328-15ucBAS":
        cap = BaslerDevice_a2A5328_15ucBAS()
    elif device.product == "acA5472-17uc":
        cap = BaslerDevice_acA5472_17uc()
    elif device.vendor == "Allied Vision":
        cap = AVTDevice(device.path)
    else:
        cap = cv.VideoCapture(device.path, device.backend)

    if cap is None or not cap.isOpened():
        raise OSError("Could not open camera stream.")

    results, cap = configure_stream(cap, resolution, codec="MJPG")
    actual_resolution = results["resolution"]

    return cap, actual_resolution
