import json
from camera import Camera

if __name__ == '__main__':
    with open('env.json') as config_file:
        config = json.load(config_file)

    RTSP_URL = f"rtsp://{config['USER']}:{config['PASS']}@{config['RTSP_URL']}"

    cam = Camera(RTSP_URL)

    while True:
        try:
            cam.show_frame()
        except AttributeError:
            pass
