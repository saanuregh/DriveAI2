from utils import WindowCapture

height = 300
width = 400
game_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
save_path = 'test/'

if __name__ == "__main__":
    current_sample = 0
    window_capture = WindowCapture(game_path, height, width)
    # TODO: rework the fps thing
    while True:
        screen = window_capture.screenshot()
        path = f"{save_path}img{current_sample}.jpg"
        screen.save(path, 'JPEG', quality=90)
        current_sample += 1
