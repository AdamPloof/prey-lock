from tkinter import *
from tkinter import ttk
import json

from interface.detection_zone_monitor import DetectionZoneMonitor
from interface.camera_feed import Camera

class PreyLockUI:
    DEFAULT_WINDOW_SIZE = "800x600"
    ASPECT_RATIO = (16, 9, 16, 9)

    def __init__(self) -> None:
        self.edit_zone_edit_active = False
        self.edit_zone_id = None

        with open(DetectionZoneMonitor.CONFIG_PATH, 'r') as f:
            self.config = json.load(f)

        # Can't initialize tk Vars until the root component is ready, so these are just placeholders.
        # see build_ui for where these are initialized.
        self.movement_status = None # tk.StringVar
        self.sensitivity_val = None # tk.DoubleVar

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

        # Binding detection events to mainframe even though the event is dispatched by the detector so that
        # we bubble the event up.
        self.movement_status = StringVar()
        self.movement_status.set('No motion detected')
        mainframe.bind("<<detect>>", self.update_detection_status)

        self.detection_zone = DetectionZoneMonitor(mainframe)

        self.zone_select_btn = ttk.Button(mainframe, text='Edit Detection Zone', command=self.toggle_detection_zone_edit)
        self.zone_select_btn.grid(column=0, row=5, rowspan=2, sticky=(W, N))

        self.capture_btn = ttk.Button(mainframe, text='Capture', command=self.capture_frame)
        self.capture_btn.grid(column=0, row=5, rowspan=2, sticky=N)

        self.motion_detected_label = ttk.Label(mainframe, textvariable=self.movement_status)
        self.motion_detected_label.grid(row=5, stick=(N, E))

        self.sensitivity_val = DoubleVar()
        sense = self.config['sensitivity'] * 1000
        self.sensitivity_val.set(sense)
        sensitivity_label = ttk.Label(mainframe, text="Sensitivity")
        sensitivity_label.grid(column=0, row=7, pady=(12, 0), sticky=W)

        self.sensitivity = ttk.Scale(
            mainframe,
            orient=HORIZONTAL,
            length=400,
            from_=1.0,
            to=100.0,
            variable=self.sensitivity_val,
            command=self.set_sensitivity
        )
        self.sensitivity.grid(column=0, row=8, columnspan=8, sticky=W)

        sensitivity_amt_label = ttk.Label(mainframe, textvariable=self.sensitivity_val)
        sensitivity_amt_label.grid(column=0, row=8, sticky=E)

    def stream_camera(self):
        self.detection_zone.refresh_monitor()
        self.detection_zone.detect()
        self.root.after(Camera.FPS_MS, self.stream_camera)

    def toggle_detection_zone_edit(self):
        if not self.edit_zone_edit_active:
            self.detection_zone.activate()
            self.edit_zone_edit_active = True
        else:
            self.detection_zone.deactivate()
            self.edit_zone_edit_active = False

    def capture_frame(self):
        self.detection_zone.capture_frame()

    def update_detection_status(self, e):
        if self.detection_zone.motion_detected:
            self.movement_status.set('Motion detected!')
        else:
            self.movement_status.set('No motion detected!')

    # Actual sensitivty range used by motion detector is between .001 and .1 but
    # the scale widget's range is 1 to 100. So that's why we move the decimal place.
    def set_sensitivity(self, e):
        sense = self.sensitivity_val.get() / 1000
        self.detection_zone.set_detector_sensitivity(sense)

        config_path = DetectionZoneMonitor.CONFIG_PATH
        with open(config_path, 'r') as f:
            config = json.load(f)

        config['sensitivity'] = sense

        with open(config_path, 'w') as out:
            json.dump(config, out)

    def run(self):
        self.root.mainloop()


def main():
    ui = PreyLockUI()
    ui.stream_camera()
    ui.run()


if __name__ == "__main__":
    main()
