import sys

from win32api import GetFileVersionInfo
import mss
from PIL import Image
from win32gui import FindWindow, IsWindow, GetWindowRect
from win32api import GetAsyncKeyState
from inputs import get_gamepad
from threading import Thread


# https://stackoverflow.com/questions/31118877/get-application-name-from-exe-file-in-python
def get_file_description(windows_exe):
    try:
        language, codepage = GetFileVersionInfo(
            windows_exe, '\\VarFileInfo\\Translation')[0]
        string_file_info = u'\\StringFileInfo\\%04X%04X\\%s' % (
            language, codepage, "FileDescription")
        description = GetFileVersionInfo(windows_exe, string_file_info)
    except:
        sys.exit("Executable doesnt exist!!!")
    return description


# Citation: Box Of Hats (https://github.com/Box-Of-Hats )
KEY_LIST = ["\b"]
for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789,.'£$/\\":
    KEY_LIST.append(char)


def key_check():
    keys = []
    for i in range(1, 256):
        if GetAsyncKeyState(i):
            keys.append(chr(i).capitalize())
    return keys


# * Forgot credit
class WindowCapture(object):
    hwnd = None
    mss_instance = None
    height = None
    width = None

    def __init__(self, title, height, width):
        self.hwnd = FindWindow(None, title)
        self.height = height
        self.width = width

    def exists(self):
        return IsWindow(self.hwnd)

    def get_size(self):
        x1, y1, x2, y2 = GetWindowRect(self.hwnd)
        x, y, w, h = x1, y1, x2 - x1, y2 - y1
        return x, y, w, h

    def screenshot(self):
        x, y, w, h = self.get_size()
        area = {"left": x + 10, "top": y + 30,
                "width": w - 20, "height": h - 40}
        if self.mss_instance is None:
            self.mss_instance = mss.mss()
        sct_img = self.mss_instance.grab(area)
        img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
        img = img.resize((self.width, self.height), Image.BICUBIC)
        return img


# Solution from https://raw.githubusercontent.com/kevinhughes27/TensorKart/master/utils.py
class XboxController(object):
    MAX_TRIG_VAL = 255
    MAX_JOY_VAL = 32768

    def __init__(self):
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0
        self._monitor_thread = Thread(target=self._monitor_controller, args=(),daemon=True)
        self._monitor_thread.start()

    def read(self):
        return self.LeftJoystickX, self.RightTrigger, self.LeftTrigger

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                    if self.LeftJoystickX == 0.999969482421875:
                        self.LeftJoystickX = 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.X = event.state
                elif event.code == 'BTN_WEST':
                    self.Y = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state
