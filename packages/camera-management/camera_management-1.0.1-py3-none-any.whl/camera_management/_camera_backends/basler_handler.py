import logging

import cv2 as cv
import numpy as np
from pypylon import pylon


class BaslerDeviceBase(cv.VideoCapture):
    def __init__(self):
        super().__init__()
        self.cap = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.cap.Open()
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        if self.cap is None:
            logging.warning("Unable to open external Basler camera.")
        self.resolution = None
        self._native_resolution = None
        # Init base class
        self.hdr_exposures = None
        self.cap.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def set(self, arg, val):
        """
        This function is the pylon equivalent to the OpenCV class function VideoCapture.set(). It is here for a proper
        transition from OpenCV to pylon. From the outside it can take all the same parameters as the OpenCV function, but
        it uses pylon-calls internally, or at least that's the goal.
        :param arg: OpenCV parameter to be set.
        :param val: The value it should be set to.
        """

        match arg:
            case cv.CAP_PROP_FRAME_WIDTH:
                self.resolution[0] = int(val)
                # self.cap.Width.SetValue(val)
            case cv.CAP_PROP_FRAME_HEIGHT:
                self.resolution[1] = int(val)
                # self.cap.Height.SetValue(val)
            case cv.CAP_PROP_FOURCC:
                pass
            case cv.CAP_PROP_AUTO_EXPOSURE:
                self.AutoExposure = val
            case cv.CAP_PROP_FPS:
                self.fps = val
            case cv.CAP_PROP_GAIN:
                self.gain = val
            case _:
                raise TypeError(f"Setting {arg} is not implemented for this {self.cap.DeviceInfo} device.")

    def get(self, arg) -> int | tuple[str, int] | float:
        """
        This function is the pylon equivalent to the OpenCV class function VideoCapture.get(). It is here for a proper
        transition from OpenCV to pylon. From the outside it can take all the same parameters as the OpenCV function, but
        it uses pylon-calls internally, or at least that's the goal.
        :param arg: OpenCV parameter to be gotten.
        :return: The value of the property.
        """
        match arg:
            case cv.CAP_PROP_FRAME_WIDTH:
                # return self.cap.Width.GetValue()
                return self.resolution[0]
            case cv.CAP_PROP_FRAME_HEIGHT:
                # return self.cap.Height.GetValue()
                return self.resolution[1]
            case cv.CAP_PROP_FOURCC:
                return int.from_bytes(b"MJPG", "little")
            case cv.CAP_PROP_AUTO_EXPOSURE:
                return self.AutoExposure
            case cv.CAP_PROP_FPS:
                return self.fps
            case cv.CAP_PROP_GAIN:
                return self.gain
            case _:
                raise TypeError(f"Setting {arg} is not implemented for this {self.cap.DeviceInfo} device.")

    @property
    def AutoExposure(self) -> tuple[str, int]:
        """
        Returns if auto exposure is enabled.
        :return: If AutoExposure is turned on and the value it is set to.
        """
        return self.cap.ExposureAuto.GetValue(), self.cap.AutoTargetBrightness.GetValue()

    @AutoExposure.setter
    def AutoExposure(self, val):
        """
        Set AutoExposureValue.
        :param val: The value it should be set to. Must be between 0 and 1.
        """
        if 1 >= val >= 0:
            self.cap.AutoTargetBrightness.SetValue(val)
        else:
            raise TypeError("Auto Brightness must be between 0 and 1.")
        # Turn on auto exposure
        self.cap.ExposureAuto.SetValue("Continuous")

    def isOpened(self) -> bool:
        """
        Check if the connection to the camera is opened.
        :return: If the connection is opened.
        """
        if self.cap is None:
            return False
        return True

    @property
    def fps(self) -> int:
        """
        Returns the frame rate limit.
        :return: Frame rate limit in frames/second.
        """
        return self.cap.AcquisitionFrameRate.GetValue()

    @fps.setter
    def fps(self, val):
        """
        Sets frame rate limit.
        :param fps: Upper FPS bound.
        """
        self.cap.AcquisitionFrameRateEnable.Value = True
        self.cap.AcquisitionFrameRate.SetValue(val)

    @property
    def throughputMode(self) -> str:
        """
        Check if the DeviceLinkThroughputLimitMode is activated.
        :return: The mode. Can be 'on' or 'Off'.
        """
        return self.cap.DeviceLinkThroughputLimitMode.GetValue()

    @throughputMode.setter
    def throughputMode(self, val):
        """
        Set the DeviceLinkThroughputLimitMode to either 'On' or 'Off'.
        :param val: The Mode to be set.
        """
        if val not in ["On", "Off"]:
            raise TypeError("ThroughputMode can only be 'On' or 'Off'.")
        self.cap.DeviceLinkThroughputLimitMode.SetValue(val)

    @property
    def autoGain(self) -> str:
        """
        Check if AutoGain is activated.
        :return: The mode. Can be 'Once' or 'TODO: FIND VALUES THAT CAN BE SET'.
        """
        return self.cap.GainAuto.GetValue()

    @autoGain.setter
    def autoGain(self, val):
        """
        Set the AutoGain Mode.
        :param val: The mode that should be set.
        """
        if val not in ["Once"]:
            raise TypeError("AutoGain can only be 'Once' or 'TODO: FIND VALUES THAT CAN BE SET'.")
        self.cap.GainAuto.SetValue(val)

    @property
    def gain(self) -> float:
        """
        Returns the set gain value.
        :return: The set value for the Gain.
        """
        return self.cap.Gain.GetValue()

    @gain.setter
    def gain(self, gain):
        """
        Turns off AutoGain and then sets a gain value manually.
        :param gain: The gain to be set. Must be between 0 and 1.
        """
        if 1 >= gain >= 0:
            self.cap.GainAuto.SetValue("Off")
            self.cap.Gain.SetValue(gain)
        else:
            raise TypeError("Gain must be between 0 and 1.")

    @property
    def roi_size(self) -> tuple[int, int]:
        """
        Returns a tuple (width, height) whcih describes the ROI in pixel. See https://docs.baslerweb.com/image-roi for more documentation.
        :return: A tuple of image width and image height.
        """
        roi = (self.cap.Width.GetValue(), self.cap.Height.GetValue())
        return roi

    @roi_size.setter
    def roi_size(self, val: tuple[int, int]):
        """
        Sets the image resolution of a region of interest.
        :param val: A tuple containing the image width and heigth.
        """
        self.cap.Width.SetValue(val[0])
        self.cap.Height.SetValue(val[1])

    @property
    def acquisitionMode(self) -> str:
        """
        Get the set AcquisitionMode.
        :return: The AcquisitionMode.
        """
        return self.cap.AcquisitionMode.GetValue()

    @acquisitionMode.setter
    def acquisitionMode(self, val: str):
        """
        Set the AcquisitionMode. Should be "SingleFrame" or "Continuous".
        :param val: The AcquisitionMode.
        """
        if val not in ["SingleFrame", "Continuous"]:
            raise TypeError('AcquisitionMode can only be "SingleFrame" or "Continuous".')
        self.cap.AcquisitionMode.SetValue(val)

    @property
    def pixelDepthMode(self) -> str:
        """
        Get pixel depth mode of sensor values.
        :return: The pixel depth mode.
        """
        return self.cap.BslSensorBitDepthMode.GetValue()

    @pixelDepthMode.setter
    def pixelDepthMode(self, val):
        """
        Set pixel depth mode of sensor values.
        :param val: The pixel depth mode.
        """
        if val not in ["Auto", "Manual"]:
            raise TypeError('BslSensorBitDepthMode can only be "Auto" or "Manual".')
        self.cap.BslSensorBitDepthMode.SetValue(val)

    @property
    def pixelDepth(self) -> str:
        """
        Get pixel depth of sensor values.
        :return: The pixel depth mode.
        """
        return self.cap.BslSensorBitDepth.GetValue()

    @pixelDepth.setter
    def pixelDepth(self, val: str):
        """
        Set the pixel depth of the sensor. Should be one of: TODO: FIND OUT.
        :param val: The pixel depth.
        """
        # if val not in [8, 10, 12]:
        # raise TypeError("BslSensorBitDepth can only be TODO: FIND OUT.")
        if self.pixelDepthMode == "Auto":
            self.pixelDepthMode = "Manual"
        self.cap.BslSensorBitDepth.SetValue(val)

    @property
    def pixelFormat(self) -> str:
        """
        get the pixel Format if the pixel depth mode is set to 'Auto'
        :return: The pixel format.
        """
        return self.cap.PixelFormat.GetValue()

    @pixelFormat.setter
    def pixelFormat(self, val: str):
        """
        Set the pixel Format if the pixel depth mode is set to 'Auto'
        :param val: The pixel format.
        """
        self.cap.PixelFormat.setValue(val)

    def setExposure(self, exposure):
        """
        ADD DOCUMENTATION AND TURN TO PROPERTY
        """
        # Set auto exposure off
        self.cap.ExposureAuto.SetValue("Off")
        # Set exposure value in microseconds
        self.cap.ExposureTime.SetValue(exposure)
        self.exposure = exposure

    def getExposure(self) -> float:
        """
        ADD DOCUMENTATION AND TURN TO PROPERTY
        """
        # Returns exposure value in microseconds
        return self.cap.ExposureTime.GetValue()

    def read(self, timeout=5000) -> tuple[bool, np.array]:
        """
        Main function of interacting with the camera. Reads the latest image from the image buffer.
        :param timeout: Waiting time in s.
        :return: A tuple containing a boolean value if the grab was successful and the actual grabbed image.
        """
        try:
            grabResult = self.cap.RetrieveResult(timeout, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():
                image = self.converter.Convert(grabResult)
                frame = image.GetArray()
                grabResult.Release()
                return True, cv.resize(frame, self.resolution, interpolation=cv.INTER_LINEAR)
        except SystemError as e:
            logging.warning(e)
            self.quit_and_open()
            return False, None

    def viewCameraStream(self):
        """
        Display live video data.
        """

        cv.namedWindow("Basler Machine Vision Stream", cv.WINDOW_AUTOSIZE)

        while self.cap.IsGrabbing():
            _, img = self.read()
            cv.imshow("Basler Machine Vision Stream", img)
            c = cv.waitKey(1)
            if c != -1:
                # When everything done, release the capture
                self.cap.StopGrabbing()
                cv.destroyAllWindows()
                break

    def release(self):
        """
        Close camera connection.
        """
        self.cap.Close()

    def quit_and_open(self):
        """
        Close and re-open camera connection.
        """
        # Close camera
        self.cap.Close()
        # Create new capture
        self.cap = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.cap.Open()

    def getStatus(self):
        """
        Saves all parameters of the camera.
        """
        pylon.FeaturePersistence.Save("Basler_Specs.txt", self.cap.GetNodeMap())


class BaslerDevice_a2A5328_15ucBAS(BaslerDeviceBase):
    def __init__(self):
        super().__init__()
        self.resolution = [5328, 4608]  # resolution of the output image
        self._native_resolution = [5328, 4608]  # resolution of the actual camera sensor in pixels


class BaslerDevice_acA5472_17uc(BaslerDeviceBase):
    def __init__(self):
        super().__init__()
        self.resolution = [5472, 3648]  # resolution of the output image
        self._native_resolution = [5472, 3648]  # resolution of the actual camera sensor in pixels
