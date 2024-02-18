import queue
import threading
import time
import uuid
from queue import Empty, Queue

import cv2 as cv
import numpy as np


class Frame:
    def __init__(self, image_data: np.ndarray) -> None:
        self.data: np.ndarray = image_data
        self.timestamp: int = time.time_ns()


class CameraThread(threading.Thread):
    """
    Custom thread for handling a OpenCV VideoCapture device.
    @param cap         OpenCV VideoCapture handle
    @param name        Optional name for the thread. If not provided, a generic unique one is created.
    @param stop_event  Optional handle for a stop event. If None is provided, an internal is created.
    @param verbose     More debug output at runtime. default arg is False.
    @param autostart   If true, start the thread immediately after creation. default arg is True.
    @param sync_barrier If given, wait for the barrier to fetch new image. Can be dangerous, as many capturing devices have internal buffers,
                        which - if not continuously collected, will add more latency than expected from the barrier. Default: None.
    """

    def __init__(
        self,
        cap: cv.VideoCapture,
        name: str = None,
        stop_event: threading.Event = None,
        sync_barrier: threading.Barrier = None,
        verbose: bool = False,
        autostart: bool = True,
        timeout: float = 2,
    ):
        super().__init__(daemon=True, name=name)
        # # self.logger = get_logger(f"tools.ct.{name}")

        if verbose:
            pass
            # self.logger.setLevel(logging.DEBUG)

        if cap is None or not cap.isOpened():
            raise OSError("Could not open camera stream.")

        if stop_event is None:
            self.stop_event = threading.Event()
        else:
            self.stop_event = stop_event
        self._cap: cv.VideoCapture = cap
        self.maxsize = 2

        # Threadsafe buffer as interface
        self._queue: Queue[Frame] = Queue(self.maxsize)
        self._commands: Queue[tuple] = Queue(50)
        self._responses = {}
        self._mutex = threading.Lock()
        self._timeout = timeout
        self.verbose = verbose
        self.sync_barrier = sync_barrier

        if autostart:
            self.start()

    def _update_image(self, image):
        """
        Put the newest frame in the queue & discard old elements, that were not collected.
        """
        try:
            self._queue.put_nowait(Frame(image))
        except queue.Full:
            pass

    def get_frame(self) -> Frame:
        """
        Get last frame
        """
        retries = 3
        frame = None
        while retries > 0:
            try:
                frame = self._queue.get(block=True, timeout=1.0)
                break
            except Empty:
                pass
                # self.logger.warning(f"{self.name}: Queue was empty. Retry: #{4 - retries}/3")

            retries -= 1

        return frame

    def _check_commands(self):
        """
        Receives the get/set commands and creates responses.
        """
        while not self._commands.empty():
            var, mode, uid = self._commands.get(block=True, timeout=1.0)
            if mode == "set":
                arg, val = var

                try:
                    self._cap.set(arg, val)
                    resp = self._cap.get(arg)
                    with self._mutex:
                        self._responses[uid] = (0, {arg: resp})
                except Exception as e:
                    with self._mutex:
                        self._responses[uid] = (-1, str(e))

            else:
                try:
                    resp = self._cap.get(var)
                    with self._mutex:
                        self._responses[uid] = (0, resp)
                except Exception as e:
                    with self._mutex:
                        self._responses[uid] = (-1, str(e))

    def run(self):
        """
        Running loop of the thread.
        """
        # self.logger.debug("Starting")
        fps = 0
        frames = 0
        while not self.stop_event.is_set():
            self._check_commands()

            start = time.time()
            success, img = self._cap.read()
            if success:
                if self.verbose:
                    frames += 1
                    time_diff = time.time() - start
                    cur_fps = 1.0 / time_diff
                    frames = 100 if frames > 100 else frames
                    fps = (fps * (frames - 1) + cur_fps) / frames
                    print(fps)
                    # self.logger.debug(f"{self.name}: {time_diff * 1000:5.2f}, {fps:5.2f}")
                self._update_image(img)
            elif not self._cap.isOpened():
                raise OSError("VideoCapture Device was unexpectedly closed")

            if self.sync_barrier is not None:
                self.sync_barrier.wait()

        self._cap.release()
        # self.logger.debug("Stopped")

    def set_cap(self, arg: int, val):
        """
        Set a camera setting.

        :param arg: The setting to ask for encoded as an enum. Available enums are listed in the documentation.
        :param val: The value you want to set it to.
        """
        uid = uuid.uuid4()
        self._commands.put(((arg, val), "set", uid), timeout=1.0)
        timeout = time.time() + self._timeout
        while time.time() < timeout:
            try:
                with self._mutex:
                    resp = self._responses[uid]
                    self._responses.pop(uid)
                return resp
            except KeyError:
                time.sleep(0.001)
                continue
        return -1

    def get_cap(self, arg: int):
        """
        Get a camera setting.

        :param arg: The setting to ask for encoded as an enum. Available enums are listed in the documentation.
        """
        uid = uuid.uuid4()
        self._commands.put(((arg), "get", uid), timeout=1.0)
        timeout = time.time() + self._timeout
        while time.time() < timeout:
            try:
                with self._mutex:
                    resp = self._responses[uid]
                    self._responses.pop(uid)
                return resp
            except KeyError:
                time.sleep(0.001)
                continue
        return -1

    def stop(self):
        """
        Set stop = True, ending the running loop.
        Call OBJECT.join() afterwards, to wait for the thread to finish.
        """
        # self.logger.debug("Stopping")
        self.stop_event.set()
