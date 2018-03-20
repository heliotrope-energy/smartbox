from smartbox.sb_tracker import SmartBoxTracker
from smartbox.sb_light import SmartBoxLight
from smartbox.sb_charge_controller import SmartBoxChargeController
from smartbox.sb_camera import SmartBoxCamera
import time, datetime
import pandas as pd

tracker = SmartBoxTracker()
light = SmartBoxLight()
controller = SmartBoxChargeController()
camera = SmartBoxCamera()
data_frame = pd.DataFrame()

while True:
    ew_position = tracker.get_ew_position()
    ns_position = tracker.get_ns_position()
    ew_moving = tracker.is_ew_moving()
    ns_moving = tracker.is_ns_moving()

    data = controller.get_all_data()
    img = camera.get_image()
    dt = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    image_filename = dt + ".np"
    data['filename'] = image_filename
    full_path = "/home/brawner/data_images/" + image_filename
    img.tofile(full_path)
    data['timestamp'] = dt
    data_frame = data_frame.append(data, ignore_index=True)
    data_frame.to_csv('/home/brawner/data.csv')
    time.sleep(60)
