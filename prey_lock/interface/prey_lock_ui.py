from tkinter import *
from tkinter import ttk

from interface.detection_zone_monitor import DetectionZoneMonitor
from interface.camera_feed import Camera

class PreyLockUI:
    DEFAULT_WINDOW_SIZE = "800x600"
    ASPECT_RATIO = (16, 9, 16, 9)

    def __init__(self) -> None:
        self.edit_zone_edit_active = False
        self.edit_zone_id = None

        self.root = self.init_tk()
        self.build_ui()

    def init_tk(self):
        root = Tk()
        root.aspect(*self.ASPECT_RATIO)
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

        self.detection_zone = DetectionZoneMonitor(mainframe)

        self.zone_select_btn = ttk.Button(mainframe, text='Edit Detection Zone', command=self.toggle_detection_zone_edit)
        self.zone_select_btn.grid(column=0, row=5, rowspan=2, sticky=(W, N))

        self.motion_detected_label = ttk.Label(mainframe, text='No motion detected')
        self.motion_detected_label.grid(row=5, stick=(N, E))

        sensitivity_label = ttk.Label(mainframe, text="Sensitivity")
        sensitivity_label.grid(column=0, row=7, pady=(12, 0))

        self.sensitivity = ttk.Scale(mainframe, orient=HORIZONTAL, length=200, from_=1.0, to=100.0)
        self.sensitivity.grid(column=0, row=8, sticky=(W, E), padx=40)
        self.sensitivity.set(20)

    def stream_camera(self):
        self.detection_zone.refresh_monitor()
        # self.detection_zone.detect()
        self.root.after(Camera.FPS_MS, self.stream_camera)

    def toggle_detection_zone_edit(self):
        if not self.edit_zone_edit_active:
            self.detection_zone.activate()
            self.edit_zone_edit_active = True
        else:
            self.detection_zone.deactivate()
            self.edit_zone_edit_active = False

    def run(self):
        self.root.mainloop()


def main():
    ui = PreyLockUI()
    ui.stream_camera()
    ui.run()


if __name__ == "__main__":
    main()
