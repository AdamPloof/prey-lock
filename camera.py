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

    def draw_text(self, text, color):
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        thickness = 2
        line_type = 2

        center = round(self.frame.shape[1] / 2)  - round(cv2.getTextSize(text, fontFace=font, fontScale=scale, thickness=thickness)[0][0] / 2)
        bottom_left = (center, 50)

        cv2.putText(self.frame, text, 
            org=bottom_left,
            fontFace=font,
            fontScale=scale,
            color=color,
            thickness=thickness,
            lineType=line_type
        )

    def draw_rect(self, x, y, width, height):
        top_left = (x, y)
        bottom_right = (x + width, y + height)
        cv2.rectangle(self.frame, top_left, bottom_right, (0,255, 0), 2)

    def show_frame(self):
        if self.frame_ready:
            cv2.imshow('Cam', self.frame)
        
        if cv2.waitKey(Camera.FPS_MS) == 27:
            self.clean_up()

    def get_frame(self):
        if not self.frame_ready:
            return None

        return self.frame

    def clean_up(self):
        cv2.destroyAllWindows()
        sys.exit()

