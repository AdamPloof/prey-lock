import json
from camera import Camera
import time
from motion_detector import MotionDetector

def main():
    with open('env.json') as config_file:
        config = json.load(config_file)

    RTSP = f"rtsp://{config['USER']}:{config['PASS']}@{config['RTSP_URL']}"

    cam = Camera(RTSP)
    detector = MotionDetector()
    detector.debug = True
    frame_cnt = 0

    while True:
        try:
            frame = cam.get_frame()
            frame_cnt += 1

            # Have detector only checking difference every n number of frames.
            if frame_cnt % cam.FPS == 0:
                detector.load_frame(frame)

            if detector.movement_detected():
                cam.draw_text('Movement detected!', (0, 255, 0))
            else:
                cam.draw_text('No movement detected!', (255, 0, 0))

            # detector.show_diff()
            cam.show_frame()
        except AttributeError:
            pass

if __name__ == '__main__':
    main()
