from tkinter import *
from tkinter import ttk

class DetectionZoneMonitor:
    # The smallest the window can be resized to for each axis
    RESIZE_MIN_THRESHOLD = 50
    # The radius of the resize controls
    RESIZE_CNTRL_RAD = 10
    
    def __init__(self, container) -> None:
        self.canvas = Canvas(container)
        self.canvas.grid(column=0, row=0, columnspan=4, rowspan=4, sticky=(N, S, E, W), pady=(0, 12))

        self.resize_mousedown = False
        self.drag_start_x: int = -1
        self.drag_start_y: int = -1
        self.drag_current_x: int = -1
        self.drag_current_y: int = -1

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

        top = (((coords[0] + coords[2]) / 2) - self.RESIZE_CNTRL_RAD, coords[1] - self.RESIZE_CNTRL_RAD, ((coords[0] + coords[2]) / 2) + self.RESIZE_CNTRL_RAD, coords[1] + self.RESIZE_CNTRL_RAD)
        self.resize_controls['top'] = self.canvas.create_oval(*top, fill='blue', outline='gray')

        bottom = (((coords[0] + coords[2]) / 2) - self.RESIZE_CNTRL_RAD, coords[3] + self.RESIZE_CNTRL_RAD, ((coords[0] + coords[2]) / 2) + self.RESIZE_CNTRL_RAD, coords[3] - self.RESIZE_CNTRL_RAD)
        self.resize_controls['bottom'] = self.canvas.create_oval(*bottom, fill='blue', outline='gray')

        left = (coords[0] + self.RESIZE_CNTRL_RAD, ((coords[1] + coords[3]) / 2) + self.RESIZE_CNTRL_RAD, coords[0] - self.RESIZE_CNTRL_RAD, ((coords[1] + coords[3]) / 2) - self.RESIZE_CNTRL_RAD)
        self.resize_controls['left'] = self.canvas.create_oval(*left, fill='blue', outline='gray')

        right = (coords[2] + self.RESIZE_CNTRL_RAD, ((coords[1] + coords[3]) / 2) + self.RESIZE_CNTRL_RAD, coords[2] - self.RESIZE_CNTRL_RAD, ((coords[1] + coords[3]) / 2) - self.RESIZE_CNTRL_RAD)
        self.resize_controls['right'] = self.canvas.create_oval(*right, fill='blue', outline='gray')

    def listen_for_resize(self):
        for cntrl in self.resize_controls.values():
            self.canvas.tag_bind(cntrl, '<ButtonPress-1>', self.mousedown)
            self.canvas.tag_bind(cntrl, '<ButtonRelease-1>', self.mouseup)

            def resize_handler(event, self=self, cntrl=cntrl):
                return self.resize_detection_zone(event, cntrl)

            self.canvas.tag_bind(cntrl, '<B1-Motion>', resize_handler)
        
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

    # TODO: Prevent resizing beyond the width of the canvas.
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

    def resize_x(self, amt, cntrl):
        new_coords = list(self.canvas.coords(self.detection_zone))
        if self.resize_controls['left'] == cntrl:
            new_coords[0] += amt
        else:
            new_coords[2] += amt

        # Prevent user from resizing beyond the min threshold size
        if (new_coords[2] - new_coords[0]) < self.RESIZE_MIN_THRESHOLD:
            return

        self.canvas.coords(self.detection_zone, *new_coords)
        self.canvas.move(cntrl, amt, 0)
        self.center_resize_cntrls('x')

    def resize_y(self, amt, cntrl):
        new_coords = list(self.canvas.coords(self.detection_zone))
        if self.resize_controls['top'] == cntrl:
            new_coords[1] += amt
        else:
            new_coords[3] += amt

        # Prevent user from resizing beyond the min threshold size
        if (new_coords[3] - new_coords[1]) < self.RESIZE_MIN_THRESHOLD:
            return

        self.canvas.coords(self.detection_zone, *new_coords)
        self.canvas.move(cntrl, 0, amt)
        self.center_resize_cntrls('y')

    # TODO: Clean this up?
    def center_resize_cntrls(self, axis: str):
        center_coords = self.canvas.coords(self.detection_zone)
        if axis == 'x':
            # Recenter x controls
            center_x = round((center_coords[0] + center_coords[2]) / 2)
            center_coords[0] = center_x
            center_coords[2] = center_x

            top_x_coords = center_coords.copy()
            top_x_coords[0] = center_coords[0] - self.RESIZE_CNTRL_RAD
            top_x_coords[1] = center_coords[1] - self.RESIZE_CNTRL_RAD
            top_x_coords[2] = center_coords[2] + self.RESIZE_CNTRL_RAD
            top_x_coords[3] = center_coords[1] + self.RESIZE_CNTRL_RAD
            self.canvas.coords(self.resize_controls['top'], *top_x_coords)

            bottom_x_coords = center_coords.copy()
            bottom_x_coords[0] = center_coords[0] - self.RESIZE_CNTRL_RAD
            bottom_x_coords[1] = center_coords[3] - self.RESIZE_CNTRL_RAD
            bottom_x_coords[2] = center_coords[2] + self.RESIZE_CNTRL_RAD
            bottom_x_coords[3] = center_coords[3] + self.RESIZE_CNTRL_RAD
            self.canvas.coords(self.resize_controls['bottom'], *bottom_x_coords)
        else:
            # Recenter y controls
            center_y = round((center_coords[1] + center_coords[3]) / 2)
            center_coords[1] = center_y
            center_coords[3] = center_y

            left_y_coords = center_coords.copy()
            left_y_coords[0] = center_coords[0] - self.RESIZE_CNTRL_RAD
            left_y_coords[1] = center_coords[1] - self.RESIZE_CNTRL_RAD
            left_y_coords[2] = center_coords[0] + self.RESIZE_CNTRL_RAD
            left_y_coords[3] = center_coords[3] + self.RESIZE_CNTRL_RAD
            self.canvas.coords(self.resize_controls['left'], *left_y_coords)

            right_y_coords = center_coords.copy()
            right_y_coords[0] = center_coords[2] - self.RESIZE_CNTRL_RAD
            right_y_coords[1] = center_coords[1] - self.RESIZE_CNTRL_RAD
            right_y_coords[2] = center_coords[2] + self.RESIZE_CNTRL_RAD
            right_y_coords[3] = center_coords[3] + self.RESIZE_CNTRL_RAD
            self.canvas.coords(self.resize_controls['right'], *right_y_coords)

