import time

from camera_management.dataclasses.aruco_dataclasses import ArucoParaSet
from camera_management.frontends.basic_frontend import manager_interface


def aruco_example(host="localhost", port=8091):
    """
    Example function to show how to get and set aruco detection settings.

    :param host: Host IP of the running ManagerApplication (see. complete_example.py on how to start)
    :param port: Port of the desired cam.
    """
    # open the manager frontend
    mgr_if = manager_interface(port=8090, host=host)

    # get the camera interface listening on port 8091
    cam = mgr_if.get_interface_by_port(port)

    # activate aruco detection
    cam.aruco_active = True

    # activate aruco drawing on output stream
    cam.aruco_draw_active = True

    # change aruco bounding box color
    cam.aruco_draw_rgb = (0, 255, 0)

    # set a different aruco parameter set
    cam.aruco_para_set = ArucoParaSet.MEDIUM_DIST

    # check if settings were applied
    print(cam.aruco_active)
    print(cam.aruco_draw_active)
    print(cam.aruco_draw_rgb)
    print(cam.aruco_para_set)

    # continuously fetch the measurement data and print it
    while True:
        print(cam.fetch_measurement_data().aruco)
        time.sleep(0.5)


if __name__ == "__main__":
    aruco_example(host="localhost", port=8091)
