"""
Run as a daemon for gathering sample images for training.
"""

import cv2
import numpy as np
import time
import json
from pathlib import Path

from detector.camera import Camera
from detector.motion_detector import MotionDetector

class Collector:
    CONFIG_PATH = "../config/detection_zone.json"    
    CAPTURE_PATH = '../captured_images'
    
    def __init__(self) -> None:
        with open('../env.json') as env_file:
            env = json.load(env_file)

        RTSP = f"rtsp://{env['USER']}:{env['PASS']}@{env['RTSP_URL']}"

        self.cam: Camera = Camera(RTSP)

        with open(self.CONFIG_PATH, 'r') as config_file:
            self.config = json.load(config_file)
        
        self.detector: MotionDetector = MotionDetector(self.config['sensitivity'])
        self.bg_reset_frames = Camera.FPS

    def crop_frame(self, frame: np.ndarray):
        frame_shape = frame.shape
        x1 = round(self.config['topleft'][0] * frame_shape[1])
        y1 = round(self.config['topleft'][1] * frame_shape[0])
        x2 = round((self.config['topleft'][0] + self.config['width']) * frame_shape[1])
        y2 = round((self.config['topleft'][1] + self.config['height']) * frame_shape[0])

        return frame[y1:y2, x1:x2]

    def get_img_filename(self) -> str:
        return Path(self.CAPTURE_PATH).joinpath(str(time.time()) + '_capture.jpg')

    # TODO: Periodically check file storage to make sure we're not exceeding a reasonable space threshold.
    def upload_img(self, frame):
        pass

    def save_image(self, frame):
        print('Saving: ' + self.get_img_filename())
        # cv2.imwrite(filename=self.get_img_filename(), img=frame)

    # TODO: Restrict frequency of save on detect motion by time.
    def run(self):
        if not self.cam.frame_ready:
            # Warm up the camera stream
            time.sleep(1)
            self.run()
            return

        frame: np.ndarray = None
        processed_cnt = 0
        while True:
            frame = self.cam.get_frame()

            if processed_cnt == 0 or processed_cnt % self.bg_reset_frames == 0:
                self.detector.set_bg_frame(frame)
                processed_cnt += 1
                continue

            self.detector.set_compare_frame(frame)
            if self.detector.movement_detected():
                self.save_image(frame)

            processed_cnt += 1

