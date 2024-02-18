from pathlib import Path

from camera_management.camera_management_app.manager_interface import ManagerApp
from camera_management.frontends.basic_frontend import manager_interface
from camera_management.tools.create_description import create_basic_description

# To see the camera stream you have to run a viewing application in a second python process, since the OpenCV image viewer
# only runs in the main thread

# Create config files for all connected cams
create_basic_description(Path(__file__).parent / "data" / "type_configs")

# Start the manager backend with the path to your newly created .json config files, it will start on port 8090
manager_backend = ManagerApp(Path(__file__).parent / "data", autostart=True)
manager_backend.start()

# Start the manager frontend with the IP and the port of the manager backend
manager_frontend = manager_interface(host="localhost", port=8090, autostart=True)

# Get all the available cams (all the cams connected to the manager device)
print(manager_frontend.get_available_cams())

# Get info on which cam is actually configured, which cam thread is started on which port and more
print(manager_frontend.get_configured_cams())

# get an actual camera interface by its port (ports start at 8091 counting upwards)
camera_interface = manager_frontend.get_interface_by_port(8091)

# use the pre-processing methods available

# set the image to black and white
camera_interface.bw = True

# un-distort the image (only available if there are calibration values present in the .json config file on the backend)
# this should result in a warning, since the above generated description files do not contain calibration values
camera_interface.undistort = True

# rotate the image by +90 degrees
camera_interface.rotate = 90
