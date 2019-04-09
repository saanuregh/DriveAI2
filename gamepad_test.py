from utils import XboxController

with XboxController() as c:
    while True:
        print(c.read())
