from tkinter import *
from PIL import Image, ImageDraw, ImageTk
from typing import Callable
import numpy as np


class DetectionZone:
    MIN_WIDTH = 50
    MIN_HEIGHT = 50
    COLOR = (150, 250, 150, 150)
    TAG = 'dzone'

    def __init__(self, canvas: Canvas, rel_topleft: tuple, rel_width: float, rel_height: float) -> None:
        self.canvas = canvas
        self.rel_topleft = rel_topleft
        self.rel_width = rel_width
        self.rel_height = rel_height

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.last_canvas_dim = (canvas_width, canvas_height)
        x = round(self.rel_topleft[0] * canvas_width)
        y = round(self.rel_topleft[1] * canvas_height)

        self.topleft = (x, y)
        self.width = round(self.rel_width * canvas_width)
        self.height = round(self.rel_height * canvas_height)

        self.ready = False
        self.is_hidden = False
        self.detection_zone: int = None
        self.img: Image.Image = None
        self.photo_img: ImageTk.PhotoImage = None

        self.draw()

    def update_props(func: Callable):
        def wrapper(*args):
            func(*args)
            self: DetectionZone = args[0]
            props = self.get_relative_props()
            self.rel_topleft = props['topleft']
            self.rel_width = props['width']
            self.rel_height = props['height']
        
        return wrapper

    def get_id(self):
        return self.detection_zone

    # Worth pointing out that once we assign new images to our img_ref properties the garbage collector will remove
    # the previous ones. The only thing we need to manually clean up is the previous detection zone canvas item.
    def draw(self):
        self.img = Image.new('RGBA', (self.width, self.height), color=self.COLOR)
        self.photo_img = ImageTk.PhotoImage(self.img)
        detection_zone = self.canvas.create_image(self.topleft, image=self.photo_img, anchor='nw', tags=self.TAG)
        if self.detection_zone is not None:
            self.canvas.delete(self.detection_zone)

        self.detection_zone = detection_zone

        if not self.ready:
            self.ready = True

    # returns True if requires redraw, false if no redraw required.
    # Feels a little hacky to return a status like this but it's a simple solution to the problem
    # of knowing when to rebind events in the DetectionZoneMonitor.
    def show(self) -> bool:
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        current_canvas_dim = (canvas_width, canvas_height)

        # Check if canvas was resized since the detection zone was hidden
        if (current_canvas_dim != self.last_canvas_dim):
            self.draw()
            redraw_required = True
        else:
            redraw_required = False

        self.canvas.itemconfigure(self.TAG, state='normal')
        self.last_canvas_dim = current_canvas_dim
        self.is_hidden = False

        return redraw_required

    def hide(self):
        self.canvas.itemconfigure(self.TAG, state='hidden')
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.last_canvas_dim = (canvas_width, canvas_height)
        self.is_hidden = True

    # Redraw the detection zone image. Most useful when the canvas is resized.
    # TODO: this is pretty laggy. Could look into optimizing this.
    def update(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = round(self.rel_topleft[0] * canvas_width)
        y = round(self.rel_topleft[1] * canvas_height)

        self.topleft = (x, y)
        self.width = round(self.rel_width * canvas_width)
        self.height = round(self.rel_height * canvas_height)

        if not self.is_hidden:
            self.draw()

    @update_props
    def resize(self, side, amt):
        props = self.get_absolute_props()
        if side == 'left':
            resize_amt = amt
            resize_amt *= -1
            resize_amt = self.restrict_resize_amt(resize_amt, side)
            topleft = (props['topleft'][0] - resize_amt, props['topleft'][1])
        elif side == 'top':
            resize_amt = amt
            resize_amt *= -1
            resize_amt = self.restrict_resize_amt(resize_amt, side)
            topleft = (props['topleft'][0], props['topleft'][1] - resize_amt)
        elif side == 'right' or side == 'bottom':
            resize_amt = amt
            resize_amt = self.restrict_resize_amt(resize_amt, side)
            topleft = props['topleft']
        else:
            raise Exception(f'Invalid side for resizing. Side: {side}')

        if side == 'top' or side == 'bottom':
            self.height += resize_amt
        else:
            self.width += resize_amt

        self.topleft = topleft
        self.draw()

    @update_props
    def move(self, amt_x, amt_y):
        move_x = self.restrict_move_amt(amt_x, 'x')
        move_y = self.restrict_move_amt(amt_y, 'y')
        self.canvas.move(self.detection_zone, move_x, move_y)

    def center(self) -> tuple:
        topleft = self.canvas.coords(self.detection_zone)
        return (
            topleft[0] + round(self.img.width / 2),
            topleft[1] + round(self.img.height / 2),
        )

    def sides(self) -> dict:
        topleft = self.canvas.coords(self.detection_zone)
        sides = {
            'top': topleft[1],
            'bottom': topleft[1] + self.img.height,
            'left': topleft[0],
            'right': topleft[0] + self.img.width
        }
        for k, v in sides.items():
            sides[k] = int(v)
        
        return sides

    #  Return the properties of detection zone relative to the canvas size.
    def get_relative_props(self) -> dict:
        def compress_prop(prop):
            compressed_prop = prop
            if prop < 0:
                compressed_prop = 0
            elif prop > 1:
                compressed_prop = 1

            return compressed_prop

        abs_center = self.center()
        abs_sides = self.sides()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        rel_center = (
            compress_prop(abs_center[0] / canvas_width),
            compress_prop(abs_center[1] / canvas_height)
        )
        rel_sides = {
            'top': compress_prop(abs_sides['top'] / canvas_height),
            'bottom': compress_prop(abs_sides['bottom'] / canvas_height),
            'left': compress_prop(abs_sides['left'] / canvas_width),
            'right': compress_prop(abs_sides['right'] / canvas_width),
        }
        rel_width = compress_prop(self.img.width / canvas_width)
        rel_height = compress_prop(self.img.height / canvas_height)

        props = {
            'center': rel_center,
            'topleft': (rel_sides['left'], rel_sides['top']),
            'bottomright': (rel_sides['right'], rel_sides['bottom']),
            'width': rel_width,
            'height': rel_height,
        }

        return props

    def get_absolute_props(self) -> dict:
        sides = self.sides()
        props = {
            'center': self.center(),
            'topleft': (sides['left'], sides['top']),
            'bottomright': (sides['right'], sides['bottom']),
            'width': self.img.width,
            'height': self.img.height,
        }

        return props

    def restrict_move_amt(self, amt, axis):
        if axis == 'x':
            side = 'left' if amt < 0 else 'right'
        else:
            side = 'top' if amt < 0 else 'bottom'

        sides = self.sides()
        boundries = self.canvas_boundries()
        boundry_sides = {
            'left': 0,
            'top': 1,
            'right': 2,
            'bottom': 3
        }

        if side == 'left' or side == 'top':
            if sides[side] + amt < boundries[boundry_sides[side]]:
                move_amt = (0 - sides[side])
            else:
                move_amt = amt
        else:
            if sides[side] + amt > boundries[boundry_sides[side]]:
                move_amt = boundries[boundry_sides[side]] - sides[side]
            else:
                move_amt = amt

        return move_amt


    def restrict_resize_amt(self, amt, side):
        sides = self.sides()
        boundries = self.canvas_boundries()

        if side == 'left':
            resize_amt = amt if (sides['left'] - amt) >= boundries[0] else self.max_resize_amt('left')
        elif side == 'top':
            resize_amt = amt if (sides['top'] - amt) >= boundries[1] else self.max_resize_amt('top')
        elif side == 'right':
            resize_amt = amt if (sides['right'] + amt) <= boundries[2] else self.max_resize_amt('right')
        elif side == 'bottom':
            resize_amt = amt if (sides['bottom'] + amt) <= boundries[3] else self.max_resize_amt('bottom')

        if side == 'left' or side == 'right':
            if self.width + resize_amt < self.MIN_WIDTH:
                resize_amt = (self.width - self.MIN_WIDTH) * -1
        else:
            if self.height + resize_amt < self.MIN_HEIGHT:
                resize_amt = (self.height - self.MIN_HEIGHT) * -1

        return resize_amt
        

    def max_resize_amt(self, side):
        sides = self.sides()        
        boundries = self.canvas_boundries()
        boundry_sides = {
            'left': 0,
            'top': 1,
            'right': 2,
            'bottom': 3
        }

        max_resize = boundries[boundry_sides[side]] - sides[side]

        if side == 'top' or side == 'left':
            max_resize = max_resize * -1 if max_resize < 0 else 0
        else:
            max_resize = max_resize if max_resize > 0 else 0

        return max_resize

    def canvas_boundries(self) -> tuple:
        left = 0
        top = 0
        right = left + self.canvas.winfo_width()
        bottom = top + self.canvas.winfo_height()

        return (left, top, right, bottom)
