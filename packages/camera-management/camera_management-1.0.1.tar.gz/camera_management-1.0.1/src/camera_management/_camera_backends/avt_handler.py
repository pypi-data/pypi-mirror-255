import copy
import logging
import threading

import cv2 as cv
import numpy as np

try:
    import vmbpy
except ImportError as e:
    raise e

logger = logging.getLogger("camera_management.avt_handler")


class AVTDevice(cv.VideoCapture):
    """
    Class for an AVT-Device such as the Allied Vision Cameras.
    """

    def __init__(self, cam_id):
        """
        Cam setup and start are executed here.
        @param cam_id: ID of the camera (see https://github.com/alliedvision/VmbPy/blob/main/vmbpy/camera.py for more info on how to access the camera ID)
        """
        super().__init__()
        self.resolution = [1920, 1080]  # Has to be set manually once to initialize the starting black image
        self.camera_id = cam_id

        self.frame = [cv.cvtColor(np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8), cv.COLOR_RGB2BGR)]
        self.stop = [False]
        self.handler = self._Handler(self.frame, self.stop)
        self.open = False
        self.killswitch = threading.Event()

        self.streaming_thread = threading.Thread(
            name="Streaming Thread", daemon=False, target=self._start_streaming_thread, kwargs={"handler": self.handler}
        )
        self.open = True
        self.streaming_thread.start()

    def _start_streaming_thread(self, handler):
        logger.info(f"Trying to start Thread and connect so {self.camera_id}!")
        with vmbpy.VmbSystem.get_instance() as vmb:
            cam = vmb.get_camera_by_id(self.camera_id)
            try:
                with cam:
                    cam.start_streaming(handler=handler)
                    self.killswitch.wait()
                    cam.stop_streaming()

            except vmbpy.VmbCameraError:
                raise vmbpy.VmbCameraError
        logger.info(f"{vmb.get_version()} terminated.")

    class _Handler:
        def __init__(self, last_frame, stop):
            self.shutdown_event = threading.Event()
            self.last_frame = last_frame
            self.stop = stop

        def __call__(self, cam: vmbpy.Camera, stream: vmbpy.Stream, frame: vmbpy.Frame):
            if frame.get_status() == vmbpy.FrameStatus.Complete:
                # print('{} acquired {}'.format(cam, frame), flush=True)
                # Convert frame if it is not already the correct format
                if frame.get_pixel_format() == vmbpy.PixelFormat.Bgr8:
                    display = copy.deepcopy(frame)
                else:
                    # This creates a copy of the frame. The original `frame` object can be requeued
                    # safely while `display` is used
                    display = copy.deepcopy(frame)
                    display = display.convert_pixel_format(vmbpy.PixelFormat.Bgr8)

                self.last_frame[0] = display
            cam.queue_frame(frame)

    def _setup_camera(self, cam):
        # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
        try:
            stream = cam.get_streams()[0]
            stream.GVSPAdjustPacketSize.run()

            while not stream.GVSPAdjustPacketSize.is_done():
                pass

        except (AttributeError, vmbpy.VmbFeatureError):
            pass

        cam_formats = cam.get_pixel_formats()
        opencv_display_format = vmbpy.PixelFormat.Bgr8

        cam_color_formats = vmbpy.intersect_pixel_formats(cam_formats, vmbpy.COLOR_PIXEL_FORMATS)
        convertible_color_formats = tuple(f for f in cam_color_formats if opencv_display_format in f.get_convertible_formats())

        cam_mono_formats = vmbpy.intersect_pixel_formats(cam_formats, vmbpy.MONO_PIXEL_FORMATS)
        convertible_mono_formats = tuple(f for f in cam_mono_formats if opencv_display_format in f.get_convertible_formats())

        if opencv_display_format in cam_formats:
            cam.set_pixel_format(opencv_display_format)

        # else if existing color format can be converted to OpenCV format do that
        elif convertible_color_formats:
            cam.set_pixel_format(convertible_color_formats[0])

        # fall back to a mono format that can be converted
        elif convertible_mono_formats:
            cam.set_pixel_format(convertible_mono_formats[0])

        logger.info("Setup done!")

    def set(self, arg, val):
        """
        This function is the pylon equivalent to the OpenCV class function VideoCapture.set(). It is here for a proper
        transition from OpenCV to pylon. From the outside it can take all the same parameters as the OpenCV function, but
        it uses pylon-calls internally, or at least that's the goal.
        :param arg: OpenCV parameter to be set.
        :param val: The value it should be set to.
        """
        if arg == cv.CAP_PROP_FRAME_WIDTH:
            self.resolution[0] = val
            # self.cap.Width.SetValue(val)
        if arg == cv.CAP_PROP_FRAME_HEIGHT:
            self.resolution[1] = val
            # self.cap.Height.SetValue(val)
        if arg == cv.CAP_PROP_FOURCC:
            pass

    def get(self, arg):
        """
        This function is the pylon equivalent to the OpenCV class function VideoCapture.get(). It is here for a proper
        transition from OpenCV to pylon. From the outside it can take all the same parameters as the OpenCV function, but
        it uses pylon-calls internally, or at least that's the goal.
        :param arg: OpenCV parameter to be gotten.
        :return: The value of the property.
        """
        if arg == cv.CAP_PROP_FRAME_WIDTH:
            # return self.cap.Width.GetValue()
            return self.resolution[0]
        if arg == cv.CAP_PROP_FRAME_HEIGHT:
            # return self.cap.Height.GetValue()
            return self.resolution[1]
        if arg == cv.CAP_PROP_FOURCC:
            return int.from_bytes(b"MJPG", "little")

    def read(self, timeout=5000):
        """
        Main function of interacting with the camera. Reads the latest image from the image buffer.
        :param timeout: Waiting time in s.
        :return: A tuple containing a boolean value if the grab was successful and the actual grabbed image.
        """
        if isinstance(self.frame[0], np.ndarray):
            return True, self.frame[0]
        else:
            ret = self.frame[0].convert_pixel_format(vmbpy.PixelFormat.Bgr8)
            return True, cv.resize(ret.as_opencv_image(), self.resolution)

    def isOpened(self) -> bool:
        """
        Return the opening state of the camera
        """
        return self.open

    def viewCameraStream(self):
        """
        Display live video data.
        """
        cv.namedWindow("Machine Vision Stream", cv.WINDOW_AUTOSIZE)

        while True:
            _, img = self.read()
            cv.imshow("Machine Vision Stream", img)
            c = cv.waitKey(1)
            if c != -1:
                # When everything done, release the capture
                cv.destroyAllWindows()
                break

    def release(self) -> None:
        """
        Pendant to the opencv release function. Releases the camera.
        """
        self.killswitch.set()
        self.streaming_thread.join()
        logger.info("Streaming Thread terminated.")


if __name__ == "__main__":
    AVT = AVTDevice("DEV_000F315D7190")
    AVT.viewCameraStream()
