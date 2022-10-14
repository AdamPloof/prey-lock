import cv2
import threading
import time
import sys


class Camera():
    def __init__(self, src):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        self.frame_ready = False
        self.frame = None
        self.previous_frame = None

        # FPS = 1/x
        # X = desired FPS
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)

        # Start frame retrieval thread
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                (ret, raw_frame) = self.capture.read()
                self.frame = self.prepare_frame(raw_frame)
                
            if not self.frame_ready:
                self.frame_ready = True

            time.sleep(self.FPS)

    def show_frame(self):
        if self.frame_ready:
            cv2.imshow('Cam', self.frame)
        
        if cv2.waitKey(self.FPS_MS) == 27:
            self.clean_up()

    def get_frame(self):
        if not self.frame_ready:
            return None

        return self.frame

    def prepare_frame(self, frame):
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prepared_frame =  cv2.GaussianBlur(frame_bw, ksize=(5, 5), sigmaX=0)

        return prepared_frame

    def clean_up(self):
        cv2.destroyAllWindows()
        sys.exit()

