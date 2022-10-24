import json
import time
from camera import Camera
from motion_detector import MotionDetector
from cat_classifier import CatClassifier

def main():
    with open('env.json') as config_file:
        config = json.load(config_file)

    RTSP = f"rtsp://{config['USER']}:{config['PASS']}@{config['RTSP_URL']}"

    cam = Camera(RTSP)
    detector = MotionDetector()
    detector.debug = True

    classifier = CatClassifier()

    frame_cnt = 0
    movement_detected: bool = False
    while True:
        try:
            frame = cam.get_frame()
            frame_cnt += 1

            # Have detector only checking difference every so many frames.
            if frame_cnt % (cam.FPS / 2) == 0:
                detector.load_frame(frame)
                movement_detected = detector.movement_detected()

                # TODO: The classifier should probably be operating in its own thread.
                if movement_detected:
                    classifier.load_frame(frame)
                    classifier.save_img()

            if movement_detected:
                cam.draw_text('Movement detected!', (0, 255, 0))
            else:
                cam.draw_text('No movement detected!', (255, 0, 0))

            # detector.show_diff()
            cam.show_frame()
        except AttributeError:
            pass

if __name__ == '__main__':
    main()
