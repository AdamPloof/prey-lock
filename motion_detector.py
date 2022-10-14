import cv2
import numpy as np

class MotionDetector():
    def __init__(self):
        self.current_frame = None
        self.prev_frame = None

        self.compare_ready = False
        self.thresh_frame = None
        self.kernel = np.ones((5, 5))

    # TODO: Loading the frame this way is causing problems. Was hoping to wait to optimize, but I think
    # we need to figure out a more reliable way of getting frames from the camera.
    def load_frame(self, frame):
        if self.current_frame is not None:
            self.prev_frame = self.current_frame

        self.current_frame = frame

    def compare(self):
        if self.prev_frame is None:
            return

        diff_frame = cv2.absdiff(self.prev_frame, self.current_frame)
        diff_frame = self.dilute(diff_frame)

        # Only take different areas that are different enough (>20 / 255)
        self.thresh_frame = cv2.threshold(diff_frame, thresh=20, maxval=255, type=cv2.THRESH_BINARY)[1]
        
        if not self.compare_ready:
            self.compare_ready = True

    def show_diff(self):
        if not self.compare_ready:
            return

        cv2.imshow('Movement', self.thresh_frame)

        if cv2.waitKey(self.FPS_MS) == 27:
            self.clean_up()


    # Dilute the image a bit to make differences more seeable; more suitable for contour detection
    def dilute(self, frame):
        diluted_frame = cv2.dilate(frame, self.kernel, 1)
        return diluted_frame