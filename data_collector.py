import os
import sys
import time

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
        self.paused = False
        self.current_sample = 0
        self.last_time = 0
        self.window_capture = WindowCapture(game_path, height, width)
        self.controller = XInputListener()
        self.keyboard = KeyboardListener()
        self.speed_server = SpeedOutputListener(hostname, port)
        self.csv_file = open(os.path.join(save_dir, "data.csv"), 'w+')
        self.start()

    def start(self):
        self.controller.start()
        self.keyboard.start()
        self.speed_server.start()
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
                path = os.path.join(
                    save_dir, f"img{self.current_sample}.jpg")
                screen.save(path, 'JPEG', quality=90)
                self.csv_file.write(f'{steering_angle:f},{throttle:f},{brake:f},{speed:f},{path}\n')
                print(f'{steering_angle},{throttle},{brake},{speed},{path}')
                # print(f'FPS:{(1/(time.time()-self.last_time)):.2f}')
                self.current_sample += 1
                self.last_time = time.time()
        print("Batch Complete!!!")
        self.stop()

    def stop(self):
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
    DataCollector('0.0.0.0', 4915)
