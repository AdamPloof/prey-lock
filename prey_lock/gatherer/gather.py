"""
Run as a daemon for gathering sample images for training.
"""

import cv2
import numpy as np
import time
import json

from detector.camera import Camera
from detector.motion_detector import MotionDetector

class Gatherer:
    CONFIG_PATH = "../config/detection_zone.json"    
    CAPTURE_PATH = '../captured_images'
    
    def __init__(self) -> None:
        with open('../env.json') as env_file:
            env = json.load(env_file)

        RTSP = f"rtsp://{env['USER']}:{env['PASS']}@{env['RTSP_URL']}"

        self.cam: Camera = Camera(RTSP)

        with open(self.CONFIG_PATH, 'r') as config_file:
            config = json.load(config_file)
        
        self.detector: MotionDetector = MotionDetector(config['sensitivity'])
        self.bg_reset_frames = Camera.FPS

    def crop_frame(self, frame):
        pass

    def save_image(self, frame):
        pass

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
                print('Motion detected!')

            processed_cnt += 1

