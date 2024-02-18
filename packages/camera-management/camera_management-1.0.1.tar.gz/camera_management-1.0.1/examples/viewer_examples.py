import pickle

import cv2
import requests


def image_viewer_requests(port: int, host="localhost"):
    """
    This is the most basic form of a viewer. It continually requests the current frame from a given address
    """
    while True:
        try:
            response = requests.get(f"http://{host}:{port}/data/imageProcessor")
        except requests.exceptions.ConnectionError:
            continue
        if response.status_code == 200:
            cv2.imshow("Stream", pickle.loads(response.content).image)
            if cv2.waitKey(20) == ord("q"):
                break


def image_viewer_interface(port: int, host="localhost"):
    """
    This is an image viewer which uses the basic frontends "fetch_data" function.
    """
    from camera_management.frontends.basic_frontend import manager_interface

    manager_frontend = manager_interface(port=8090, host=host)
    camera_interface = manager_frontend.get_interface_by_port(port)

    while True:
        data = camera_interface.fetch_image_data()
        cv2.imshow("Stream", data.image)
        if cv2.waitKey(20) == ord("q"):
            break


if __name__ == "__main__":
    # image_viewer_requests(port=8092)
    image_viewer_interface(port=8091)
