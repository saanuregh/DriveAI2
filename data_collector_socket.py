import os
import sys
import time
from queue import Queue
from threading import Thread
import socket
import asyncio

from utils import WindowCapture, XInputListener, KeyboardListener, SpeedOutputListener

# * Game Path (to exe)
game_path = "D:/Games/Grand Theft Auto V/GTA5.exe"

# * Resolution of capture
height = 300
width = 400

# * Training data parameters
save_dir = 'training_data/teat/'
# samples_per_batch = 36000  # 1 batch equals 1 hour of gameplay
samples_per_batch = 100  # 1 batch equals 1 hour of gameplay
samples_per_sec = 10
wait_time = (1 / samples_per_sec)


class DataCollector(object):
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self._done = False
        self.paused = False
        self.last_time = 0
        self.window_capture = WindowCapture(game_path, height, width)
        self.controller = XInputListener()
        self.keyboard = KeyboardListener()
        self.speed_server = SpeedOutputListener('0.0.0.0', 4915)
        self.controller.start()
        self.keyboard.start()
        self.speed_server.start()
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(send())

    async def send(self):
        reader, writer = await asyncio.open_connection(self.hostname,self.port,loop=self.loop)
        print("Data collection Starting!!!")
        for i in reversed(range(1, 4)):
            print(i)
            time.sleep(1)
        while self.current_sample < samples_per_batch:
            keys = self.keyboard.read()
            if 'T' in keys:
                if self.paused:
                    print('Unpausing!!!')
                    self.paused = False
                    time.sleep(1)
                else:
                    print('Pausing!!!')
                    self.paused = True
                    time.sleep(1)
            if self.paused and 'Q' in keys:
                sys.exit("Exiting!!!")
            # Very slow >:(
            # if not self.window_capture.exists():
            #     sys.exit("Executable exited!!!")
            if not self.paused and (time.time() - self.last_time) >= wait_time:
                
                screen = self.window_capture.screenshot()
                steering_angle, throttle, brake = self.controller.read()
                if steering_angle == 0.999969482421875:
                    steering_angle = 1  # error in +x-axis max val = 0.999969482421875
                steering_angle = 0.5 + steering_angle * 0.5  # normalize between 0 and 1
                speed = self.speed_server.read()
                _data = [screen, steering_angle, throttle, brake, speed]
                writer.write(_data)
                # print(f'FPS:{(1/(time.time()-self.last_time)):.2f}')
                self.last_time = time.time()
        print("Batch Complete!!!")
        self.stop()

    def stop(self):
        self._done = True
        self.saver_thread.join()
        self.csv_file.close()
        self.speed_server.join()
        self.keyboard.join()
        self.controller.join()
        print("Exiting!!!")


if __name__ == "__main__":
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # else:
    #     print("Directory exists!!!")
    #     if input("Continue(y/n): ") != 'y':
    #         sys.exit()
    DataCollector('192.168.0.13', 4915)
