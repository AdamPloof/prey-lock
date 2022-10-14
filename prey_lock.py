import json
from camera import Camera
from motion_detector import MotionDetector

def main():
    with open('env.json') as config_file:
        config = json.load(config_file)

    RTSP = f"rtsp://{config['USER']}:{config['PASS']}@{config['RTSP_URL']}"

    cam = Camera(RTSP)
    detector = MotionDetector()

    while True:
        try:
            frame = cam.get_frame()
            detector.load_frame(frame)
            detector.compare()
            detector.show_diff()
        except AttributeError:
            pass

if __name__ == '__main__':
    main()
