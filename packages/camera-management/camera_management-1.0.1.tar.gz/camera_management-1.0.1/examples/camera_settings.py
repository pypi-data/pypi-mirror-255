from camera_management import SETTINGS
from camera_management.frontends.basic_frontend import manager_interface

# open the manager frontend
mgr_if = manager_interface()

# get the camera interface listening on port 8091
cam = mgr_if.get_interface_by_port(8091)

# set max fps to 12 and show if it was set
print(cam.set_general_setting(SETTINGS.CAP_PROP_FPS, 14))
print(cam.get_general_setting(SETTINGS.CAP_PROP_FPS))

# set auto exposure to 0.8 and show if it was set
print(cam.set_general_setting(SETTINGS.CAP_PROP_AUTO_EXPOSURE, 0.8))
print(cam.get_general_setting(SETTINGS.CAP_PROP_AUTO_EXPOSURE))

print(cam.set_general_setting(SETTINGS.CAP_PROP_FRAME_WIDTH, 400))
print(cam.get_general_setting(SETTINGS.CAP_PROP_FRAME_WIDTH))

print(cam.description)
