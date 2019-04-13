import time

import numpy
import pyvjoy

j = pyvjoy.VJoyDevice(1)

VJOY_MAX = 32768

while 1:
    for i in numpy.arange(0, 1.05, 0.05):
        j.data.wAxisX = int(i * VJOY_MAX)  # X-axis/Steering angle
        j.data.wAxisY = int(i * VJOY_MAX)  # Left Trigger/Brake
        j.data.wAxisZ = int(i * VJOY_MAX)  # Right Trigger/Throttle
        j.update()
        print(f'{i:.2f}')
        time.sleep(1)
