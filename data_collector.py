import os
import socket
import sys
import threading
import time

from utils import WindowCapture, XInputListener, KeyboardListener

# * Game Path (to exe)
game_path = "D:/Games/Grand Theft Auto V/GTA5.exe"

# * Resolution of capture
height = 300
width = 400

# * Training data parameters
save_dir = 'training_data/teat/'
samples_per_batch = 36000  # 1 batch equals 1 hour of gamplay
samples_per_sec = 10
wait_time = (1 / samples_per_sec)


class DataCollector(object):
    def __init__(self, hostname, port):
        self.speed = 0
        self.hostname = hostname
        self.port = port
        self.paused = False
        self.current_sample = 0
        self.last_time = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.window_capture = WindowCapture(game_path, height, width)
        self.controller = XInputListener()
        self.keyboard = KeyboardListener()
        self.csv_file = open(os.path.join(save_dir, "data.csv"), 'w+')
        self._get_speed_thread = threading.Thread(
            target=self._get_speed, args=(), daemon=True)

    def start(self):
        print("Waiting for SpeedOutput connection!!!")
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)
        self.conn, self.address = self.socket.accept()
        print("SpeedOutput connection established!!!")
        self._get_speed_thread.start()
        print("Data collection Starting!!!")
        for i in reversed(range(1, 4)):
            print(i)
            time.sleep(1)

        while self.current_sample < samples_per_batch:
            self.keys = self.keyboard.read()
            if 'T' in self.keys:
                if self.paused:
                    print('Unpausing!!!')
                    self.paused = False
                    time.sleep(1)
                else:
                    print('Pausing!!!')
                    self.paused = True
                    time.sleep(1)
            if self.paused and 'Q' in self.keys:
                sys.exit("Exiting!!!")
            if not self.window_capture.exists():
                sys.exit("Executable exited!!!")
            if not self.paused and (time.time() - self.last_time) >= wait_time:
                self.screen = self.window_capture.screenshot()
                self.steering_angle, self.throttle, self.brake = self.controller.read()
                if self.steering_angle == 0.999969482421875:
                    self.steering_angle = 1  # error in +x-axis max val = 0.999969482421875
                self.steering_angle = 0.5 + self.steering_angle * 0.5  # normalize between 0 and 1
                self.path = os.path.join(
                    save_dir, f"img{self.current_sample}.jpg")
                self.screen.save(self.path, 'JPEG', quality=90)
                self.csv_file.write(
                    f'{self.steering_angle},{self.throttle},{self.brake},{self.speed},{self.path}\n')
                # print(f'{self.steering_angle},{self.throttle},{self.brake},{self.speed},{self.path}')
                # print(f'FPS:{(1/(time.time()-self.last_time)):.2f}')
                self.current_sample += 1
                self.last_time = time.time()
        sys.exit("Batch Complete!!!")

    def _get_speed(self):
        print("SpeedOutput monitoring thread started!!!")
        while True:
            self.speed_data = self.conn.recv(25)
            if self.speed_data is not None:
                self.speed = float(
                    str(self.speed_data, 'utf-8', errors='namereplace')[11:23])


if __name__ == "__main__":
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    else:
        print("Directory exists!!!")
        if input("Continue(y/n): ") != 'y':
            sys.exit()
    collector = DataCollector("localhost", 4915)
    collector.start()
