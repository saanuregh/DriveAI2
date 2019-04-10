from time import sleep

from utils import XInputListener, KeyboardListener

if __name__ == '__main__':
    controller = XInputListener()
    keyboard = KeyboardListener()
    while True:
        print(keyboard.read(), controller.read())
        sleep(1)
