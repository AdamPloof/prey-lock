import cv2
import numpy as np
import sys
from camera import Camera

class MotionDetector():
    def __init__(self):
        self.CONTOUR_SIZE_THRESH = 50
        # The percentage of pixels in the image that have "moved" at which motion is considered detected.
        self.MOTION_THRESHOLD_PERCENT = .025

        self.debug = False
        self.current_frame = None
        self.prev_frame = None

        self.compare_ready = False
        self.kernel = np.ones((6, 6))

    def load_frame(self, frame):
        if self.current_frame is not None:
            self.prev_frame = self.current_frame

        self.current_frame = frame

    def get_threshold(self):
        if self.prev_frame is None:
            return None

        diff_frame = cv2.absdiff(self.prev_frame, self.current_frame)
        diff_frame = self.dilute(diff_frame)

        # Only take different areas that are different enough (>20 / 255)
        thresh_frame = cv2.threshold(diff_frame, thresh=20, maxval=255, type=cv2.THRESH_BINARY)[1]

        return thresh_frame

    # Dilute the image a bit to make differences more seeable; more suitable for contour detection
    def dilute(self, frame):
        diluted_frame = cv2.dilate(frame, self.kernel, 1)
        return diluted_frame

    def show_diff(self):
        thresh_frame = self.get_threshold()
        if thresh_frame is None:
            return

        cv2.imshow('Movement', thresh_frame)

        if cv2.waitKey(Camera.FPS_MS) == 27:
            self.clean_up()

    def movement_detected(self):
        thresh_frame = self.get_threshold()
        if thresh_frame is None:
            return False
        
        pixels_moved = thresh_frame[thresh_frame == 255].size
        percent_moved = pixels_moved / thresh_frame.size

        if self.debug:
            if percent_moved > self.MOTION_THRESHOLD_PERCENT:
                print('Motion detected. Percent moved: ' + str(percent_moved))
            else:
                print('No motion detected. Percent moved: ' + str(percent_moved))

        return percent_moved > self.MOTION_THRESHOLD_PERCENT


    def clean_up(self):
        cv2.destroyAllWindows()
        sys.exit()