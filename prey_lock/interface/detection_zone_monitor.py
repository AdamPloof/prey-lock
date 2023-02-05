from tkinter import *
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
import numpy as np
import cv2
import threading
from queue import Queue
from pathlib import Path
from datetime import datetime
import time
import json

from interface.detection_zone import DetectionZone
from detector.camera import Camera
from detector.motion_detector import MotionDetector

class DetectionZoneMonitor:
    CONFIG_PATH = "../config/detection_zone.json"    
    RESIZE_MIN_THRESHOLD = 50 # The smallest the window can be resized to for each axis
    RESIZE_CNTRL_RAD = 10 # The radius of the resize controls
    CNTRL_TAG = 'dz_cntrl'
    DZ_COLOR = (150, 250, 150, 150)
    DETECTION_RESET_TIME = 2 # In seconds
    CAPTURE_PATH = '../captured_images'
    
    def __init__(self, container) -> None:
        self.canvas = Canvas(container, background='#e8e9eb')
        self.canvas.grid(column=0, row=0, columnspan=4, rowspan=4, sticky=(N, S, E, W), pady=(0, 12))

        self.resize_mousedown = False
        self.drag_start_x: int = -1
        self.drag_start_y: int = -1
        self.drag_current_x: int = -1
        self.drag_current_y: int = -1

        self.detection_zone: DetectionZone = None
        self.resize_controls: dict = {
            'top': None,
            'bottom': None,
            'left': None,
            'right': None,
        }

        with open('../env.json') as env_file:
            env = json.load(env_file)

        RTSP = f"rtsp://{env['USER']}:{env['PASS']}@{env['RTSP_URL']}"

        self.cam = Camera(RTSP)
        self.stream: int = None
        self.frame = None
        self.frame_img = None
        self.frame_photo_img = None

        self.frame_queue = Queue(maxsize=10)
        self.cam_thread = threading.Thread(target=self.fetch_camera_frame, args=())
        self.cam_thread.daemon = True
        self.cam_thread.start()

        with open(self.CONFIG_PATH, 'r') as f:
            config = json.load(f)

        self.detector: MotionDetector = MotionDetector(config['sensitivity'])
        # self.detector.debug = True
        self.detector_frame_cnt = 0
        self.motion_detected = False

    def fetch_camera_frame(self):
        # Warm up the camera stream
        if not self.cam.frame_ready:
            time.sleep(1)
            self.fetch_camera_frame()
            return
    
        while True:
            self.frame_queue.put(self.cam.get_frame())

    def refresh_monitor(self):
        if self.frame_queue.empty():
            return
        else:
            self.frame = self.frame_queue.get()

        self.frame_img = Image.fromarray(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
        self.frame_img = self.frame_img.resize((self.canvas.winfo_width(), self.canvas.winfo_height()))
        self.frame_photo_img = ImageTk.PhotoImage(self.frame_img)
        stream = self.canvas.create_image((0, 0), image=self.frame_photo_img, anchor='nw')

        if self.detection_zone is not None and self.detection_zone.get_id() is not None:
            self.canvas.tag_lower(stream, self.detection_zone.get_id())

        if self.stream is not None:
            self.canvas.delete(self.stream)

        self.stream = stream

    def detect(self):
        if not self.detection_zone:
            return

        refresh_bg = False
        frame = self.crop_frame(self.frame)
        if self.detector_frame_cnt % (self.DETECTION_RESET_TIME * Camera.FPS) == 0:
            self.detector.set_bg_frame(frame)
            refresh_bg = True
        else:
            self.detector.set_compare_frame(frame)

        self.detector_frame_cnt += 1

        if refresh_bg == True:
            self.motion_detected = False
        elif self.detector.movement_detected():
            self.motion_detected = True
        else:
            self.motion_detected = False

        self.canvas.master.event_generate("<<detect>>")

    def crop_frame(self, frame: np.ndarray):
        frame_shape = frame.shape
        x1 = round(self.detection_zone.rel_topleft[0] * frame_shape[1])
        y1 = round(self.detection_zone.rel_topleft[1] * frame_shape[0])
        x2 = round((self.detection_zone.rel_topleft[0] + self.detection_zone.rel_width) * frame_shape[1])
        y2 = round((self.detection_zone.rel_topleft[1] + self.detection_zone.rel_height) * frame_shape[0])

        # Inspect the cropped frame
        # cv2.imshow('Test Crop', frame[y1:y2, x1:x2])

        # if cv2.waitKey(Camera.FPS_MS) == 27:
        #     cv2.destroyAllWindows()

        return frame[y1:y2, x1:x2]


    def scale_detection_zone(self, event):
        self.detection_zone.update()
        self.bind_detection_zone_events()

        w_delta = (event.width - self.last_canvas_dim[0])
        h_delta = (event.height - self.last_canvas_dim[0])
        if w_delta != 0 or h_delta != 0:
            self.center_resize_cntrls()

        self.last_canvas_dim = (event.width, event.height)

    def move_detection_zone(self, e):
        if self.drag_start_x == -1 or self.drag_start_y == -1:
            return

        self.drag_current_x = e.x
        amt_x = self.drag_current_x - self.drag_start_x
        self.drag_start_x = e.x

        self.drag_current_y = e.y
        amt_y = self.drag_current_y - self.drag_start_y
        self.drag_start_y = e.y
        
        self.detection_zone.move(amt_x, amt_y)
        self.bind_detection_zone_events()
        self.center_resize_cntrls()

    def draw_resize_controls(self):
        cntrls = self.resize_cntrl_coords()
        for k, pos in cntrls.items():
            tag = 'x_cntrl' if k == 'left' or k == 'right' else 'y_cntrl'
            self.resize_controls[k] = self.canvas.create_oval(*pos, fill='blue', outline='gray', tags=(self.CNTRL_TAG, tag))

        self.canvas.tag_bind('x_cntrl', '<Enter>', self.cursor_resize_x)
        self.canvas.tag_bind('x_cntrl', '<Leave>', self.cursor_default)

        self.canvas.tag_bind('y_cntrl', '<Enter>', self.cursor_resize_y)
        self.canvas.tag_bind('y_cntrl', '<Leave>', self.cursor_default)
        self.listen_for_resize()

    def center_resize_cntrls(self):
        cntrls = self.resize_cntrl_coords()
        self.canvas.coords(self.resize_controls['top'], *cntrls['top'])
        self.canvas.coords(self.resize_controls['bottom'], *cntrls['bottom'])
        self.canvas.coords(self.resize_controls['left'], *cntrls['left'])
        self.canvas.coords(self.resize_controls['right'], *cntrls['right'])

        detection_zone_id = self.detection_zone.get_id()
        for cntrl in self.resize_controls.values():
            self.canvas.tag_raise(cntrl, detection_zone_id)

    def resize_cntrl_coords(self) -> dict:
        center = self.detection_zone.center()
        sides = self.detection_zone.sides()
        top = (
            center[0] - self.RESIZE_CNTRL_RAD, # x0
            sides['top'] - self.RESIZE_CNTRL_RAD, #y0
            center[0] + self.RESIZE_CNTRL_RAD, #x1
            sides['top'] + self.RESIZE_CNTRL_RAD #y1
        )

        bottom = (
            center[0] - self.RESIZE_CNTRL_RAD, # x0
            sides['bottom'] - self.RESIZE_CNTRL_RAD, #y0
            center[0] + self.RESIZE_CNTRL_RAD, #x1
            sides['bottom'] + self.RESIZE_CNTRL_RAD #y1
        )

        left = (
            sides['left'] - self.RESIZE_CNTRL_RAD, # x0
            center[1] - self.RESIZE_CNTRL_RAD, #y0
            sides['left'] + self.RESIZE_CNTRL_RAD, #x1
            center[1] + self.RESIZE_CNTRL_RAD #y1
        )

        right = (
            sides['right'] - self.RESIZE_CNTRL_RAD, # x0
            center[1] - self.RESIZE_CNTRL_RAD, #y0
            sides['right'] + self.RESIZE_CNTRL_RAD, #x1
            center[1] + self.RESIZE_CNTRL_RAD #y1
        )

        return {
            'top': top,
            'bottom': bottom,
            'left': left,
            'right': right,
        }

    # Note that these cursors are native Mac OS X cursors. If this is to be cross platform will need to deal with this.
    # TODO: Set cursor to grabbing on move and resize while resizing even if cursor leaves the resize cntrl during drag.
    def cursor_resize_x(self, e):
        self.canvas.config(cursor='resizeleftright')

    def cursor_resize_y(self, e):
        self.canvas.config(cursor='resizeupdown')

    def cursor_grab(self, e):
        self.canvas.config(cursor='openhand')

    def cursor_grabbing(self, e):
        self.canvas.config(cursor='closedhand')

    def cursor_default(self, e):
        self.canvas.config(cursor='')
        
    def activate(self):
        if not self.detection_zone or not self.detection_zone.ready:
            self.load_detection_zone()
            self.draw_resize_controls()
            self.last_canvas_dim = (self.canvas.winfo_width(), self.canvas.winfo_height())
        else:
            redraw_required = self.detection_zone.show()
            if redraw_required:
                self.bind_detection_zone_events()
    
            self.center_resize_cntrls()
            self.canvas.itemconfigure(self.CNTRL_TAG, state='normal')

    def deactivate(self):
        self.detection_zone.hide()
        self.canvas.itemconfigure(self.CNTRL_TAG, state='hidden')

    def mousedown(self, e):
        self.resize_mousedown = True
        self.drag_start_x = e.x
        self.drag_start_y = e.y
        self.drag_current_x = e.x
        self.drag_current_y = e.y

    def mouseup(self, e):
        self.resize_mousedown = False
        self.drag_start_x = -1
        self.drag_start_y = -1

    def listen_for_resize(self):
        for cntrl in self.resize_controls.values():
            self.canvas.tag_bind(cntrl, '<ButtonPress-1>', self.mousedown)
            self.canvas.tag_bind(cntrl, '<ButtonRelease-1>', self.mouseup)

            def resize_handler(event, self=self, cntrl=cntrl):
                return self.resize_detection_zone(event, cntrl)

            self.canvas.tag_bind(cntrl, '<B1-Motion>', resize_handler)

    def resize_detection_zone(self, e, cntrl):
        if self.drag_start_x == -1 or self.drag_start_y == -1:
            return

        # Swapping keys for values to make it easier to look up which control we're dealing with.
        cntrls = {v: k for k, v in self.resize_controls.items()}
        if cntrls[cntrl] == 'top' or cntrls[cntrl] == 'bottom':
            self.drag_current_y = e.y
            amt = self.drag_current_y - self.drag_start_y
            self.resize_y(amt, cntrl)
            self.drag_start_y = e.y
        else:
            self.drag_current_x = e.x
            amt = self.drag_current_x - self.drag_start_x
            self.resize_x(amt, cntrl)
            self.drag_start_x = e.x
        
        self.center_resize_cntrls()

    # If we wanted to, the resize_x and resize_y could be refactored into a single method. But it's fine for now.
    def resize_x(self, amt, cntrl):
        direction = 'left' if self.resize_controls['left'] == cntrl else 'right'
        self.detection_zone.resize(direction, amt)
        self.bind_detection_zone_events()

    def resize_y(self, amt, cntrl):
        direction = 'top' if self.resize_controls['top'] == cntrl else 'bottom'
        self.detection_zone.resize(direction, amt)
        self.bind_detection_zone_events()

    def bind_detection_zone_events(self):
        detection_zone_id = self.detection_zone.get_id()
        self.canvas.tag_bind(detection_zone_id, '<Enter>', self.cursor_grab)
        self.canvas.tag_bind(detection_zone_id, '<Leave>', self.cursor_default)
        self.canvas.tag_bind(detection_zone_id, '<ButtonPress-1>', self.mousedown)
        self.canvas.tag_bind(detection_zone_id, '<ButtonRelease-1>', self.mouseup)
        self.canvas.tag_bind(detection_zone_id, '<B1-Motion>', self.move_detection_zone)

    def load_detection_zone(self):
        with open(self.CONFIG_PATH, 'r') as f:
            config = json.load(f)

        self.detection_zone = DetectionZone(
            self.canvas,
            tuple(config['top_left']),
            config['width'],
            config['height']
        )
        self.detection_zone.draw()
        self.canvas.bind('<Configure>', self.scale_detection_zone)
        self.bind_detection_zone_events()

    def set_detector_sensitivity(self, sensitivity):
        self.detector.sensitivity = sensitivity

    def capture_frame(self):
        cap_file = Path(DetectionZoneMonitor.CAPTURE_PATH).joinpath(datetime.now().strftime('%Y%m%d%H%M%S') + 'capture.jpg')
        print(f'Saving file: {cap_file}')
        cv2.imwrite(filename=str(cap_file), img=self.frame)
