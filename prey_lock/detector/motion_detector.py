import cv2
import numpy as np
import sys
from detector.camera import Camera

class MotionDetector():
    def __init__(self, sensitivity):
        self.sensitivity = sensitivity
        self.debug = False
        self.bg_frame = None
        self.compare_frame = None

        self.compare_ready = False
        self.kernel = np.ones((6, 6))

    def set_bg_frame(self, frame):
        self.bg_frame = self.prepare_frame(frame) if frame is not None else frame

    def set_compare_frame(self, frame):
        self.compare_frame = self.prepare_frame(frame) if frame is not None else frame

    def prepare_frame(self, frame):
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prepared_frame =  cv2.GaussianBlur(frame_bw, ksize=(5, 5), sigmaX=0)

        return prepared_frame

    def get_threshold(self):
        if self.bg_frame is None:
            return None

        try:
            diff_frame = cv2.absdiff(self.bg_frame, self.compare_frame)
            diff_frame = self.dilute(diff_frame)

            # Only take different areas that are different enough (>20 / 255)
            thresh_frame = cv2.threshold(diff_frame, thresh=20, maxval=255, type=cv2.THRESH_BINARY)[1]
        except cv2.error as e:
            if self.debug:
                print('Unable to compare frames of different dimensions')
            return None

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

    def movement_detected(self) -> bool:
        thresh_frame = self.get_threshold()
        if thresh_frame is None:
            return False
        
        pixels_moved = thresh_frame[thresh_frame == 255].size
        percent_moved = pixels_moved / thresh_frame.size

        if self.debug:
            if percent_moved > self.sensitivity:
                print('Motion detected. Percent moved: ' + str(percent_moved))
            else:
                print('No motion detected. Percent moved: ' + str(percent_moved))

        return percent_moved > self.sensitivity


    def clean_up(self):
        cv2.destroyAllWindows()
        sys.exit()