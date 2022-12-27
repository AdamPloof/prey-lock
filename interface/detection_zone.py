from tkinter import *
from PIL import Image, ImageDraw, ImageTk
import numpy as np


class DetectionZone:
    COLOR = (150, 250, 150, 150)
    TAG = 'dzone'

    def __init__(self, width: int, height: int, topleft: tuple, canvas: Canvas) -> None:
        self.width = width
        self.height = height
        self.topleft = topleft
        self.canvas = canvas

        self.ready = False
        self.detection_zone: int = None
        self.img: Image = None
        self.photo_img: ImageTk.PhotoImage = None

        self.draw()

    def get_id(self):
        return self.detection_zone

    # Worth pointing out that once we assign new images to our img_ref properties the garbage collector will remove
    # the previous ones. The only thing we need to manually clean up is the previous detection zone canvas object.
    def draw(self):
        self.img = Image.new('RGBA', (self.width, self.height), color=self.COLOR)
        self.photo_img = ImageTk.PhotoImage(self.img)
        detection_zone = self.canvas.create_image(self.topleft, image=self.photo_img, anchor='nw', tags=self.TAG)
        if self.detection_zone is not None:
            self.canvas.delete(self.detection_zone)

        self.detection_zone = detection_zone

        if not self.ready:
            self.ready = True

    def show(self):
        self.canvas.itemconfigure(self.TAG, state='normal')

    def hide(self):
        self.canvas.itemconfigure(self.TAG, state='hidden')

    # Redraw the detection zone image. Most useful when the canvas is resized.
    def update(self):
        props = self.relative_props()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.width = round(props['width'] * canvas_width)
        self.height = round(props['height'] * canvas_height)
        self.topleft = (round(props['topleft'][0] * canvas_width), round(props['topleft'][1] * canvas_height))
        self.draw()

    def resize(self, side, amt):
        sides = self.sides()
        props = self.absolute_props()
        boundries = self.canvas_boundries()
        if side == 'top':
            resize_amt = amt if sides['top'] - amt >= boundries[1] else boundries[1]
            topleft = (props['topleft'][0], props['topleft'][1] - resize_amt)
        elif side == 'bottom':
            resize_amt = amt if sides['bottom'] + amt <= boundries[3] else boundries[3]
            topleft = props['topleft']
        elif side == 'left':
            resize_amt = amt if sides['left'] - amt >= boundries[0] else boundries[0]
            topleft = (props['topleft'][0] - resize_amt, props['topleft'][1])
        elif side == 'right':
            resize_amt = amt if sides['right'] + amt <= boundries[2] else boundries[2]
            topleft = props['topleft']
        else:
            raise Exception(f'Invalid side for resizing. Side: {side}')

        self.width += resize_amt
        self.topleft = topleft
        self.update()

    def move(self, amt_x, amt_y):
        self.canvas.move(self.detection_zone, amt_x, amt_y)

    def center(self) -> tuple:
        return (
            round(self.img.width / 2),
            round(self.img.height / 2),
        )

    def sides(self) -> dict:
        topleft = self.canvas.coords(self.detection_zone)
        return {
            'top': topleft[1],
            'bottom': topleft[1] + self.img.height,
            'left': topleft[0],
            'right': topleft[0] + self.img.width
        }

    #  Return the properties of detection zone relative to the canvas size.
    def relative_props(self) -> dict:
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
            'bottom': compress_prop(abs_center['bottom'] / canvas_height),
            'left': compress_prop(abs_center['left'] / canvas_width),
            'right': compress_prop(abs_center['right'] / canvas_width),
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

    def absolute_props(self) -> dict:
        sides = self.sides()
        props = {
            'center': self.center(),
            'topleft': (sides['left'], sides['top']),
            'bottomright': (sides['right'], sides['bottom']),
            'width': self.img.width,
            'height': self.img.height,
        }

        return props

    def canvas_boundries(self) -> tuple:
        left = 0
        top = 0
        right = left + self.canvas.winfo_width()
        bottom = top + self.canvas.winfo_height()

        return (left, top, right, bottom)
