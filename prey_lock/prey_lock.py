import json
import time
import cv2
from detector.camera import Camera
from detector.motion_detector import MotionDetector
from detector.cat_classifier import CatClassifier

def get_detector_config(cam: Camera):
    with open('./config/detector.json', 'r') as config_file:
        config = json.load(config_file)

    detection_zone = config['motion_detector']['detection_zone']

    # TODO: need to factor in x, y when figuring out max width/height
    cam_frame_width = round(cam.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    if detection_zone['width'] is None or detection_zone['width'] > cam_frame_width:
        detection_zone['width'] = cam_frame_width

    cam_frame_height = round(cam.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if detection_zone['height'] is None or detection_zone['height'] > cam_frame_height:
        detection_zone['height'] = cam_frame_height

    config['motion_detector']['detection_zone'] = detection_zone

    return config['motion_detector']

def main():
    with open('env.json') as env_file:
        env = json.load(env_file)

    RTSP = f"rtsp://{env['USER']}:{env['PASS']}@{env['RTSP_URL']}"

    cam = Camera(RTSP)
    detector = MotionDetector()
    detector.debug = True

    # TODO: configure detector
    detector_config = get_detector_config(cam)

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
                cam.draw_text('No movement detected!', (0, 0, 255))

            # detector.show_diff()
            detection_zone = detector_config['detection_zone']
            cam.draw_rect(detection_zone['x'], detection_zone['y'], detection_zone['width'], detection_zone['height'])
            cam.show_frame()
        except AttributeError:
            pass

if __name__ == '__main__':
    main()
