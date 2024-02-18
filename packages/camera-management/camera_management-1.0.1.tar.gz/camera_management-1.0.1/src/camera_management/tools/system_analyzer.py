"""
unit for analyzing the system for windows and Linux
-> not platform independent!
"""
import logging
import platform

import cv2 as cv
from pypylon import pylon

from camera_management.dataclasses.general_dataclasses import VideoDevice

logger = logging.getLogger("camera_management.system_analyzer")

try:
    import vmbpy

    vmbpy_import = True
except ImportError:
    vmbpy_import = False
    logging.warning("system_analyzer: (Ignore if you do not want to use AVT Cameras) Could not import vmbpy. See the readme for more information.")

if platform.system() == "Windows":
    from pygrabber.dshow_graph import FilterGraph
elif platform.system() == "Linux":
    import pyudev
elif platform.system() == "Darwin":
    # ----------------------------------------------------------------- system_profiler
    import plistlib
    import re

    import AVFoundation


else:
    raise NotImplementedError(f"Only Windows and Linux are supported currently. Active platform is {platform.system()}")


def check_sys_config(verbose=False) -> dict:
    """
    function to detect for system and os the current version and features
    :param verbose:
    :return:
    """
    os = platform.system()
    pc_name = platform.node()
    os_version = platform.version()
    cpu = platform.processor()
    machine_type = platform.machine()
    python_version = platform.python_version()
    # --------------------------------------------------------------------------------------------------------
    ocv_version = cv.version.opencv_version
    gpu_count = cv.cuda.getCudaEnabledDeviceCount()
    if gpu_count != 0:
        logger.warning(cv.cuda_DeviceInfo.deviceID(0))  # all GPU's or NVIDIA only?
    cpu_count = cv.getNumberOfCPUs()
    thread_count = cv.getNumThreads()
    cuda_devices = cv.cuda.getCudaEnabledDeviceCount()
    # cv.cuda_DeviceInfo.majorVersion(cv.cuda_DeviceInfo.deviceID()) )#, cv.cuda_DeviceInfo.deviceID() )
    # ---------------------------------------------------------------------------------------------------------
    availableBackends = [cv.videoio_registry.getBackendName(b) for b in cv.videoio_registry.getBackends()]

    # -------------------------------------------------- create iterable output-dictionary
    sys_config = {
        "hostname": pc_name,
        "system": {"os": os, "os version": os_version},
        "cpu": cpu,
        "machine type": machine_type,
        "CPU count": cpu_count,
        "thread count": thread_count,
        "cuda devices": cuda_devices,
        "python version": python_version,
        "opencv version": ocv_version,
        "video-_camera_backends": availableBackends,
    }
    if verbose:
        print("\n---------------------------------------------------------------------------------------------------------- get system configuration")
        print(
            f"current system configuration:\n"
            f"       Hostname:       {pc_name}\n"
            f"       System:         {os} - {os_version}\n"
            f"       CPU info:       {cpu} - type: {machine_type}\n"
            f"       CPU count:      {cpu_count} - threads: {thread_count}\n"
            f"       cuda devices:   {cuda_devices}\n"
            f"       Python version: {python_version}\n"
            f"       OpenCV version: {ocv_version}\n"
            f"       video-_camera_backends: {availableBackends}\n\n"
        )

    return sys_config


# ----------------------------------------------------------------------------------------------------------------------------------------------------
def get_connected_cams(verbose: bool = False) -> list[VideoDevice]:
    """
    returns for all supported platforms a uniform list of connected cameras
    return: list of Videodevice
    """
    current_system = platform.system()
    if current_system == "Windows":
        device_list = __get_cam_names_windows()
    elif current_system == "Linux":
        device_list = __get_cam_names_linux()
    elif current_system == "Darwin":
        device_list = __get_cam_names_mac()
    else:
        raise NotImplementedError(f"Only Windows, Darwin and Linux are supported currently. Active platform is {current_system}")

    if vmbpy_import:
        avt_devices = __get_cam_names_vimba()
        device_list.extend(avt_devices)
    basler_devices = __get_cam_names_basler()
    device_list.extend(basler_devices)

    if (verbose) and device_list is not None:
        print("\n---------------------------------------------------------------------------------------------------------- get system configuration")
        print("current system: \t", current_system)
        for idx, device in enumerate(device_list):
            print(f"\t{idx} - {device.product} - {device.serial} @ {device.path}")

    return device_list


def __get_cam_names_windows() -> list[VideoDevice]:
    """
    for Windows (based on DirectShow!):
    ->  https://github.com/bunkahle/pygrabber
    -> returns all video devices of the DShow filter graph
    """
    graph = FilterGraph()

    # ------------------------------------------------------------- force a list of strings
    device_list: list[VideoDevice] = []
    for i, device in enumerate(graph.get_input_devices()):
        dev = VideoDevice(
            path=i,
            serial=str(device),
            vendor_id=None,
            product_id=None,
            vendor="",
            product=str(device),
            backend=cv.CAP_DSHOW,
        )
        device_list.append(dev)

    logger.debug("With pygrabber and DSHOW detected camera streams:")
    for idx, device in enumerate(device_list):
        logger.debug(f"\t{idx} - {device.serial} @ {device.path}")

    return device_list


def __get_cam_names_linux() -> list[VideoDevice]:
    """
    for Linux (pure Python binding for libudev)
    -> https://pypi.org/project/pyudev/
    """
    streams: list[VideoDevice] = list()
    context = pyudev.Context()
    for device in context.list_devices(subsystem="video4linux"):
        dpath = device.get("DEVNAME", "unknown device.path")
        vendor = device.get("ID_VENDOR", "vendor not found")
        vid = device.get("ID_VENDOR_ID", "vendorId not found")
        product = device.get("ID_MODEL", "product not found")
        pid = device.get("ID_MODEL_ID", "productId not found")
        serial = device.get("ID_SERIAL", "serial not found")
        caps = device.get("ID_V4L_CAPABILITIES", "capabilities not found")

        # _logger.debug(f"Capabilities: {caps}")
        if "capture" in caps:
            dev = VideoDevice(dpath, vid, pid, vendor, product, serial, backend=cv.CAP_V4L2)
            streams.append(dev)
            # _logger.debug(dev)

    logger.debug("With udev detected capturing camera streams:")
    for idx, device in enumerate(streams):
        logger.debug(f"\t{idx} - {device.serial} @ {device.path}")

    return streams


def __get_cam_names_mac() -> list[VideoDevice]:
    """
    Python:   -> https://pypi.org/project/pyobjc-framework-AVFoundation/
    Framework -> https://developer.apple.com/documentation/avfoundation/avcapturedevice
    ffmpeg -> https://trac.ffmpeg.org/wiki/Capture/Webcam
    -> terminal command:  ffmpeg -f avfoundation -list_devices true -i ""
    -> gets a correct list of video devices, python list is equal to the terminal output
    -> the ORDER OF THE stream list is not equal to the opencv stream list (even with the same backend)!

    """
    import subprocess

    streams: list[VideoDevice] = list()
    backend = cv.CAP_AVFOUNDATION  # backend is for mac: AV-Foundation for opencv

    cmd = "system_profiler SPUSBDataType -xml"
    output = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    output = plistlib.loads(output.stdout)[0]

    # -> https://developer.apple.com/documentation/avfoundation/avcapturedevice
    # the session is the data sink for the AVCaptureDevice
    # session = AVFoundation.AVCaptureSession.alloc().init()
    # session.discoverySessionWithDeviceTypes(AVFoundation.AVMediaTypeVideo)

    # -------------------------------------------------------------------------------------------------------- get a device list
    AVF_devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo)  # only video      - Deprecated function
    # dev = AVFoundation.AVCaptureDevice.devices()                                                           # video and audio - Deprecated function

    # AVF_devices = AVFoundation.AVCaptureDevice.DiscoverySession()

    # AVF_device = None
    for idx, AVF_device in enumerate(AVF_devices):
        AVF_device.init()  # is possible but without any result
        product = AVF_device.localizedName()
        uniqueID = AVF_device.uniqueID()

        serial = None
        uid = None
        paths = tuple(find_paths(output, str(product)))

        if paths:
            for path in paths:
                path = path[:-1]
                cam = output
                for p in path:
                    cam = cam[p]
                loc_id = cam["location_id"]
                pid = cam["product_id"]
                vid = cam["vendor_id"]
                uid = str(hex(int(str(loc_id).split("/")[0].strip(), 16))) + str(vid).split("0x")[1][:4].strip() + str(pid).split("0x")[1][:4].strip()

                if uid == uniqueID:
                    serial = cam["serial_num"]
                    break
        vendor = AVF_device.manufacturer()
        model_ID = AVF_device.modelID()
        match = re.search(r"VendorID_(\d+) ProductID_(\d+)", model_ID)

        if match:
            vid = match.group(1)
            pid = match.group(2)

            vid = hex(int(vid))
            pid = hex(int(pid))
        else:
            vid = None
            pid = None

        transp_type = AVF_device.transportType().to_bytes(4, "big").decode()
        device_type = AVF_device.deviceType()
        is_used = AVF_device.isInUseByAnotherApplication()
        # -> https://github.com/phracker/MacOSX-SDKs/blob/master/MacOSX10.5.sdk/System/Library/Frameworks/IOKit.framework/Versions/A/Headers/audio/IOAudioTypes.h
        # -> https://developer.apple.com/documentation/avfoundation/avcapturedevice/1390520-deviceswithmediatype

        dev = VideoDevice(None, vid, pid, vendor, product, serial, backend, transp_type, uniqueID, device_type, is_used)
        streams.append(dev)

    # magic line, comes from:
    #    -> https://github.com/opencv/opencv/blob/224dac9427cfa1b3f1ba8787f681a3fe7f253e87/modules/videoio/src/cap_avfoundation_mac.mm#L392
    streams.sort(key=lambda x: x.unique_id)
    for idx, device in enumerate(streams):
        device.path = idx

    logger.debug("\nWith mac_AVFoundation identified capturing camera streams:")
    for idx, device in enumerate(streams):
        logger.debug(f"{device.path}: {device.product} - {device.serial} ({device.unique_id} {device.is_used}")

    return streams


def __get_cam_names_basler() -> list[VideoDevice]:
    """
    get all the connected basler cameras. Can't be found with __get_cam_names_mac_AVFoundation() since it uses a different backend
    TODO: Only the first connected cam can be found, if there are more cams connected this will have to be fixed
    """

    tlf = pylon.TlFactory.GetInstance()
    devices = tlf.EnumerateDevices()
    ret_devices = []
    for idx, d in enumerate(devices):
        logger.debug(d.GetModelName(), d.GetSerialNumber(), dir(d))
        logger.debug(d.GetAddress(), d.GetDeviceClass(), d.GetDeviceID(), d.GetFullName())
        ret_devices.append(VideoDevice(f"BAS_{idx}", None, None, "Basler", d.GetModelName(), d.GetSerialNumber(), None, None, d.GetSerialNumber()))
    return ret_devices


def __get_cam_names_vimba() -> list[VideoDevice]:
    ret_devices = []
    with vmbpy.VmbSystem.get_instance() as vmb:
        devices = vmb.get_all_cameras()

    for idx, d in enumerate(devices):
        d.set_access_mode(vmbpy.AccessMode.Full)
        logger.debug(d.get_name(), d.get_model(), d.get_access_mode(), d.get_permitted_access_modes(), d.is_streaming())
        logger.debug(d.get_id(), d.get_serial(), d.get_interface_id())
        ret_devices.append(VideoDevice(d.get_id(), None, None, "Allied Vision", d.get_name(), d.get_serial(), d.get_interface_id()))
    return ret_devices


def find_paths(nested_dict, value, prepath=()):
    """
    Finds the path to a value in a dict.

    :param nested_dict: The dict to search.
    :param value: The value to find.
    :param prepath: The path preceding the the current dict level (needed for recursion)
    """
    for k, v in nested_dict.items():
        path = prepath + (k,)

        if isinstance(v, list):  # v is list
            for i, n in enumerate(v):
                if n == value:  # found value
                    yield path
                elif hasattr(n, "items"):  # v is a dict
                    yield from find_paths(n, value, path + (i,))
        else:
            if v == value:  # found value
                yield path
            elif hasattr(v, "items"):  # v is a dict
                yield from find_paths(v, value, path)


# ====================================================================================================================================================
if __name__ == "__main__":
    get_connected_cams(verbose=True)
