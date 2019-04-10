import os
import socket
import sys
import threading
import time

from utils import WindowCapture, XInputListener, KeyboardListener

# * Game Path (to exe)
# game_path = r"D:\Games\Need for Speed - Most Wanted\NFS13.exe"
game_path = r"D:\Games\Grand Theft Auto V\GTA5.exe"
# game_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

# * Resolution of capture
height = 300
width = 400

# * Training data parameters
save_path = 'training_data/'
samples_per_batch = 20000
samples_per_sec = 10
wait_time = (1 / samples_per_sec)

if not os.path.exists(save_path):
    os.makedirs(save_path)


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
        self.csv_file = open(save_path + 'data.csv', 'w+')
        self._monitor_thread = threading.Thread(
            target=self._get_speed, args=(), daemon=True)
        self._monitor_thread.start()

    def start(self):
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)
        self.conn, self.address = self.socket.accept()
        print("Data Collection Starting!!!")
        for i in list(range(4))[::-1]:
            print(i + 1)
            time.sleep(1)
        print('STARTING!!!')

        while True:
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
                self.last_time = time.time()
                self.screen = self.window_capture.screenshot()
                self.steering_angle, self.throttle, self.brake = self.controller.read()
                self.path = f"{save_path}img{self.current_sample}.png"
                self.screen.save(self.path, 'PNG')
                self.csv_file.write('%f,%f,%f,%s,%s\n' %
                                    (self.steering_angle, self.throttle, self.brake, self.speed, self.path))
                print(
                    f'{self.path},{self.steering_angle},{self.throttle},{self.brake},{self.speed}')
                self.current_sample += 1

    def _get_speed(self):
        while True:
            try:
                self.speed_data = self.conn.recv(25)
                if self.speed_data is not None:
                    self.speed = float(
                        str(self.speed_data, 'utf-8', errors='namereplace')[11:23])
            except:
                pass


if __name__ == "__main__":
    print("Main Executing!!!")
    collector = DataCollector("localhost", 4915)
    collector.start()
