from tkinter import *
from tkinter import ttk

class DetectionZoneMonitor:
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

    # TODO: Prevent resizing beyond 0 width or height and the edge of the window.
    # Also, continually recenter controls on resize.
    def resize_detection_zone(self, e, cntrl):
        if self.drag_start_x == -1 or self.drag_start_y == -1:
            raise Exception('Drag start not registered. Something weird happened.')

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

        self.canvas.coords(self.detection_zone, *new_coords)
        self.canvas.move(cntrl, amt, 0)

    def resize_y(self, amt, cntrl):
        new_coords = list(self.canvas.coords(self.detection_zone))
        if self.resize_controls['top'] == cntrl:
            new_coords[1] += amt
        else:
            new_coords[3] += amt

        self.canvas.coords(self.detection_zone, *new_coords)
        self.canvas.move(cntrl, 0, amt)


