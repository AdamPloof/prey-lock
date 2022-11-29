from tkinter import *
from tkinter import ttk


class PreyLockUI:
    DEFAULT_WINDOW_SIZE = "800x600"

    def __init__(self) -> None:
        self.edit_zone_edit_active = False
        self.edit_zone_id = None

        self.root = self.init_tk()
        self.build_ui()

        # detection_zone coordinates normalized to 0.0 to 1.0 scale of current canvas size
        # rather than absolute pixel values. E.g. (.5, .5) would be the center of the canvas.
        self.detection_zone = {
            'topleft': (0.2, 0.2),
            'bottomright': (.8, .8)
        }
    
    def init_tk(self):
        root = Tk()
        root.title('Cat Dector')
        root.geometry(self.DEFAULT_WINDOW_SIZE)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        return root

    def build_ui(self):
        mainframe = ttk.Frame(self.root, padding='12 12 12 24')
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(5, pad=12)
        mainframe.rowconfigure(0, weight=1)

        self.canvas = Canvas(mainframe)
        self.canvas.grid(column=0, row=0, columnspan=4, rowspan=4, sticky=(N, S, E, W), pady=(0, 12))

        self.zone_select_btn = ttk.Button(mainframe, text='Edit Detection Zone', command=self.toggle_detection_zone_edit)
        self.zone_select_btn.grid(column=0, row=5, rowspan=2, sticky=(W, N))

        self.motion_detected_label = ttk.Label(mainframe, text='No motion detected')
        self.motion_detected_label.grid(row=5, stick=(N, E))

        sensitivity_label = ttk.Label(mainframe, text="Sensitivity")
        sensitivity_label.grid(column=0, row=7, pady=(12, 0))

        self.sensitivity = ttk.Scale(mainframe, orient=HORIZONTAL, length=200, from_=1.0, to=100.0)
        self.sensitivity.grid(column=0, row=8, sticky=(W, E), padx=40)
        self.sensitivity.set(20)


    def toggle_detection_zone_edit(self):
        if not self.edit_zone_edit_active:
            dzone_coodinates = self.detection_zone_coordinates()
            self.edit_zone_id = self.canvas.create_rectangle(*dzone_coodinates, fill='gray', outline='black')
            self.edit_zone_edit_active = True
        elif self.edit_zone_id is not None:
            self.canvas.delete(self.edit_zone_id)
            self.edit_zone_edit_active = False
        else:
            self.edit_zone_edit_active = False

    def detection_zone_coordinates(self):
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        top_left = (self.detection_zone['topleft'][0] * canvas_w, self.detection_zone['topleft'][1] * canvas_h)
        bottom_right = (self.detection_zone['bottomright'][0] * canvas_w, self.detection_zone['bottomright'][1] * canvas_h)
        dzone_coordinates = tuple(round(x) for x in top_left) + tuple(round(x) for x in bottom_right)

        return dzone_coordinates

    def run(self):
        self.root.mainloop()


def main():
    ui = PreyLockUI()
    ui.run()


if __name__ == "__main__":
    main()
