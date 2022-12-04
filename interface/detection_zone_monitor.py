from tkinter import *
from tkinter import ttk

class DetectionZoneMonitor:
    def __init__(self, container) -> None:
        self.canvas = Canvas(container)
        self.canvas.grid(column=0, row=0, columnspan=4, rowspan=4, sticky=(N, S, E, W), pady=(0, 12))

        # These are actually the IDs of the canvas items.
        self.detection_zone: int = None
        self.resize_controls: dict = {
            'top': None,
            'bottom': None,
            'left': None,
            'right': None,
        }

        # detection_zone_coord coordinates normalized to 0.0 to 1.0 scale of current canvas size
        # rather than absolute pixel values. E.g. (.5, .5) would be the center of the canvas.
        self.detection_zone_coord = {
            'topleft': (0.2, 0.2),
            'bottomright': (.8, .8)
        }

    def detection_zone_coordinates(self):
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        top_left = (self.detection_zone_coord['topleft'][0] * canvas_w, self.detection_zone_coord['topleft'][1] * canvas_h)
        bottom_right = (self.detection_zone_coord['bottomright'][0] * canvas_w, self.detection_zone_coord['bottomright'][1] * canvas_h)
        dzone_coordinates = tuple(round(x) for x in top_left) + tuple(round(x) for x in bottom_right)

        return dzone_coordinates

    def draw_resize_controls(self):
        coords = self.canvas.coords(self.detection_zone)

        top = (((coords[0] + coords[2]) / 2) - 10, coords[1] - 10, ((coords[0] + coords[2]) / 2) + 10, coords[1] + 10)
        self.resize_controls['top'] = self.canvas.create_oval(*top, fill='blue', outline='gray')

        bottom = (((coords[0] + coords[2]) / 2) - 10, coords[3] + 10, ((coords[0] + coords[2]) / 2) + 10, coords[3] - 10)
        self.resize_controls['bottom'] = self.canvas.create_oval(*bottom, fill='blue', outline='gray')

        left = (coords[0] + 10, ((coords[1] + coords[3]) / 2) + 10, coords[0] - 10, ((coords[1] + coords[3]) / 2) - 10)
        self.resize_controls['left'] = self.canvas.create_oval(*left, fill='blue', outline='gray')

        right = (coords[2] + 10, ((coords[1] + coords[3]) / 2) + 10, coords[2] - 10, ((coords[1] + coords[3]) / 2) - 10)
        self.resize_controls['right'] = self.canvas.create_oval(*right, fill='blue', outline='gray')

    def listen_for_resize(self):
        for cntrl in self.resize_controls.values():
            self.canvas.tag_bind(cntrl, '<B1-Motion>', self.resize_detection_zone)
        
    def activate(self):
        dzone_coodinates = self.detection_zone_coordinates()
        self.detection_zone = self.canvas.create_rectangle(*dzone_coodinates, fill='gray', outline='black')
        self.draw_resize_controls()
        self.listen_for_resize()

    def deactivate(self):
        self.canvas.delete(self.detection_zone)
        self.detection_zone = None

        for k, v in self.resize_controls.items():
            self.canvas.delete(v)
            self.resize_controls[k] = None

    # TODO: Actually resize. Can restrict the direction of resizing based on which control is being moved.
    # E.g. if the top control is moving only pay attention to the change in y.
    def resize_detection_zone(self, e):
        print(f'x: {e.x}, y: {e.y}')
