from tkinter import *
from tkinter import ttk


class PreyLockUI:
    def __init__(self) -> None:
        self.edit_zone_edit_active = False
        self.edit_zone_id = None

        self.root = Tk()
        self.root.title('Cat Dector')

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

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
            self.edit_zone_id = self.canvas.create_rectangle(0, 40, 200, 200, fill='gray', outline='black')
            self.edit_zone_edit_active = True
        elif self.edit_zone_id is not None:
            self.canvas.delete(self.edit_zone_id)
            self.edit_zone_edit_active = False
        else:
            self.edit_zone_edit_active = False


    def run(self):
        self.root.mainloop()


def main():
    ui = PreyLockUI()
    ui.run()


if __name__ == "__main__":
    main()
