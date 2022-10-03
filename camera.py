import cv2
import threading
import time
import sys


class Camera():
    def __init__(self, src):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

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
                (self.ret, self.frame) = self.capture.read()
            time.sleep(self.FPS)

    def show_frame(self):
        cv2.imshow('Cam', self.frame)
        if cv2.waitKey(self.FPS_MS) == 27:
            self.clean_up()

    def clean_up(self):
        cv2.destroyAllWindows()
        sys.exit()

