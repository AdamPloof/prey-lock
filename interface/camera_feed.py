from tkinter import *
from tkinter import ttk

import cv2
import threading
import time
import sys


class Camera():
    FPS = 30
    FPS_MS = int((1 / FPS) * 1000)

    def __init__(self, src):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        self.frame_ready = False
        self.frame = None
        self.previous_frame = None

        # Start frame retrieval thread
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                (ret, raw_frame) = self.capture.read()
                self.frame = raw_frame
                
            if not self.frame_ready:
                self.frame_ready = True

            time.sleep(1 / Camera.FPS)

    def get_frame(self):
        if not self.frame_ready:
            return None

        return self.frame

    def clean_up(self):
        cv2.destroyAllWindows()
        sys.exit()
