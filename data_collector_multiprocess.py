import os
import sys
import time
from utils import get_file_description, key_check, WindowCapture, XboxController
import socket
from threading import Thread
from multiprocessing import Process, JoinableQueue

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

queue = JoinableQueue()


class DataCollector(Process):
    def __init__(self, hostname, port):
        super(DataCollector, self).__init__()
        self.speed = 0
        self.hostname = hostname
        self.port = port
        self.paused = False
        self.last_time = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.window_capture = WindowCapture(
            get_file_description(game_path), height, width)
        self.controller = XboxController()
        self._get_speed_thread = Thread(
            target=self._get_speed, args=(), daemon=True)
        self._get_speed_thread.start()

    def run(self):
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)
        self.conn, self.address = self.socket.accept()
        print("Data Collection Starting!!!")
        for i in list(range(4))[::-1]:
            print(i + 1)
            time.sleep(1)
        print('STARTING!!!')
        while True:
            self.keys = key_check()
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
                queue.put_nowait([self.screen, self.steering_angle,
                                  self.throttle, self.brake, self.speed])
                queue.join()

    def _get_speed(self):
        while True:
            try:
                self.speed_data = self.conn.recv(25)
                if self.speed_data is not None:
                    self.speed = float(
                        str(self.speed_data, 'utf-8', errors='namereplace')[11:23])
            except:
                pass


class DataSaver(Process):
    def __init__(self):
        super(DataSaver, self).__init__()
        self.current_sample = 0
        self.csv_file = open(save_path + 'data.csv', 'w+')

    def run(self):
        print("Data Saver Starting!!!")
        while True:
            if not queue.empty():
                self.path = f"{save_path}img{self.current_sample}.png"
                self.data = queue.get_nowait()
                queue.task_done()
                self.data[0].save(self.path, 'PNG')
                self.csv_file.write('%f,%f,%f,%s,%s\n' % (
                    self.data[1], self.data[2], self.data[3], self.data[4], self.path))
                print(self.path, ",", self.data[1:])
                self.current_sample += 1


if __name__ == "__main__":
    print("Main Executing!!!")

    collector = DataCollector("localhost", 4915)
    collector.start()
    collector.join()
    saver = DataSaver()
    saver.start()
    saver.join()
