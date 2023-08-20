import tkinter as tk
from tkinter import Canvas, messagebox
from tkinter.ttk import Style, OptionMenu
import cv2
import json
import time
from PIL import Image, ImageTk
from front.pose_detector import main, run

LIGHT_MODE = {
    "bg": "white",
    "text": "black",
    "btn": "white",
    "btn_text": "black",
    "dropdown_bg": "white",
    "dropdown_text": "black",
    "highlight": "#e1e1e1"
}

DARK_MODE = {
    "bg": "black",
    "text": "white",
    "btn": "black",
    "btn_text": "white",
    "dropdown_bg": "black",
    "dropdown_text": "white",
    "highlight": "#666666"
}


class SideGUI:

    def __init__(self, root, pi_port = None, video_source=1):
        self.root = root
        self.root.title("Posture Corrector")
        self.root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        self.combo_style = Style()
        self.pi_port = pi_port
        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)
        self.detector = main()
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 2080)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 4020)

        self.label_widget = tk.Label(root, borderwidth=2, relief="solid", highlightthickness=2,
                                     highlightbackground="black")  # Initially set for LIGHT_MODE
        self.label_widget.place(relx=0.17, rely=0.05, relwidth=0.8, relheight=0.8)

        self.theme = LIGHT_MODE  # Start with light mode

        # Read data from the JSON file
        self.firstRun = True
        self.integer = 0
        self.i = 0
        self.time = time.time()
        with open('side_data.json') as json_file:
            self.loaded_data = json.load(json_file)
        self.dropdown = [self.loaded_data[0]["name"], self.loaded_data[0]["name"], self.loaded_data[1]["name"],
                         self.loaded_data[2]["name"], self.loaded_data[3]["name"]]

        self.dropdown_var = tk.StringVar()
        self.dropdown_var.set(self.loaded_data[0]["name"])

        self.btn_setup = self.create_rounded_button("Setup", "light blue", self.setup, 0.02, 0.15)
        self.dropdown = self.create_styled_combobox(0.02, 0.05)
        self.btn_start = self.create_rounded_button("Start", "light green", self.start, 0.02, 0.4)
        self.btn_stop = self.create_rounded_button("Stop", "#FF8888", self.stop, 0.02, 0.5)
        self.btn_theme_toggle = self.create_rounded_button("Toggle Theme", "grey", self.toggle_theme, 0.02, 0.7)
        self.btn_switch_to_front = self.create_rounded_button("Switch to Front", "grey", self.switch_to_front, 0.02, 0.8)

        self.is_playing = False
        self.update()

        self.apply_theme(self.theme)  # Apply theme on initialization

    def apply_theme(self, theme):
        self.root.configure(bg=theme["bg"])
        self.label_widget.configure(bg=theme["bg"], fg=theme["text"])

        button_configurations = {
            self.btn_start: "light green",
            self.btn_stop: "#FF8888",
            self.btn_setup: "light blue"
        }

        border_color = "black" if theme == LIGHT_MODE else "white"
        self.label_widget.configure(highlightbackground=border_color)

        for btn, color in button_configurations.items():
            btn.configure(bg=color)
            btn.itemconfig("rectangle", fill=color, outline=color)

        # Configuring the dropdown style
        self.combo_style.configure("TCombobox",
                                   fieldbackground=theme["dropdown_bg"],
                                   background=theme["btn"],
                                   foreground=theme["dropdown_text"],
                                   padding=10,
                                   font=("Helvetica", 12))

    def toggle_theme(self):
        if self.theme == LIGHT_MODE:
            self.theme = DARK_MODE
        else:
            self.theme = LIGHT_MODE

        self.apply_theme(self.theme)

    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, r, **kwargs):
        """ Create a rounded rectangle """
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs)

    def create_rounded_button(self, text, color, cmd, relx, rely):
        canvas = Canvas(self.root, bg=color, bd=0, highlightthickness=0, relief='ridge')
        canvas.place(relx=relx, rely=rely, relwidth=0.11, relheight=0.08)

        r = 5
        btn_shape = self.create_rounded_rectangle(canvas, 10, 10, 10 + 150, 10 + 40, r, outline=color, fill=color,
                                                  width=2)
        btn_id = canvas.create_text(80, 30, text=text, fill=self.theme["btn_text"], font=("Helvetica", 12))

        canvas.tag_bind(btn_shape, '<ButtonPress-1>', lambda event, c=cmd: c())
        canvas.tag_bind(btn_id, '<ButtonPress-1>', lambda event, c=cmd: c())

        return canvas

    def create_styled_combobox(self, relx, rely):
        combo_style = Style()
        combo_style.theme_use('clam')
        combo_style.configure("TCombobox",
                              fieldbackground=self.theme["dropdown_bg"],
                              background=self.theme["btn"],
                              foreground=self.theme["dropdown_text"],
                              padding=10,
                              font=("Helvetica", 12))
        combo = OptionMenu(self.root, self.dropdown_var, *self.dropdown)
        combo.place(relx=relx, rely=rely, relwidth=0.12)
        return combo

    def create_styled_textbox(self, relx, rely, color):
        canvas = Canvas(self.root, bg=color, bd=0, highlightthickness=0, relief='ridge')
        canvas.place(relx=relx, rely=rely, relwidth=0.11, relheight=0.08)
        entry1 = tk.Entry(self.root)
        r = 5
        btn_shape = self.create_rounded_rectangle(canvas, 10, 10, 10 + 150, 10 + 40, r, outline=color, fill=color,
                                                  width=2)
        btn_id = canvas.create_window(relx, rely, window=entry1)

        return canvas, entry1

    def start(self):
        if not self.is_playing:
            self.is_playing = True
            self.firstRun = True
            self.update()

    def stop(self):
        self.is_playing = False

    def show_popup(self):
        self.inSetup = False
        messagebox.showinfo("Config", "Submitted!")
        self.savetoJson()

    def savetoJson(self):
        self.entered_data["name"] = self.name.get()
        self.entered_data["x0"] /= self.frames 
        self.entered_data["x2"] /= self.frames
        self.entered_data["x5"] /= self.frames 
        self.entered_data["x7"] /= self.frames 
        self.entered_data["x8"] /= self.frames 
        self.entered_data["x11"] /= self.frames 
        self.entered_data["x12"] /= self.frames
        self.entered_data["y0"] /= self.frames 
        self.entered_data["y2"] /= self.frames 
        self.entered_data["y5"] /= self.frames 
        self.entered_data["y7"] /= self.frames 
        self.entered_data["y8"] /= self.frames 
        self.entered_data["y11"] /= self.frames 
        self.entered_data["y12"] /= self.frames 
        self.frames = 0
        self.text_box.destroy()
        self.popup_btn.destroy()
        print("writing to json")
        self.loaded_data.append(self.entered_data)
        with open('side_data.json', 'w') as json_file:
            json.dump(self.loaded_data, json_file, indent=4, separators=(',',':'))

    def setupRun(self):
        _, img = self.vid.read()
        self.frames+=1
        img, data, _, _ = run(img, self.i, self.detector, self.loaded_data, self.integer, True, entered_data=self.entered_data)
        opencv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        captured_image = Image.fromarray(opencv_image)
        photo_image = ImageTk.PhotoImage(image=captured_image)
        self.label_widget.photo_image = photo_image
        self.label_widget.configure(image=photo_image)
        if self.name.get() != "" and (time.time() - self.time) > 5:
            self.inSetup = False
            messagebox.showinfo("Config", "Data collection timeout, submitted!")
            self.savetoJson()
        if self.inSetup:
            self.label_widget.after(10, self.setupRun)
        else:
            return

    def setup(self):
        self.entered_data = {}
        self.time = time.time()
        self.entered_data["name"] = ""
        self.entered_data["x0"] = 0
        self.entered_data["x2"] = 0
        self.entered_data["x5"] = 0 
        self.entered_data["x7"] = 0 
        self.entered_data["x8"] = 0 
        self.entered_data["x11"] = 0
        self.entered_data["x12"] = 0
        self.entered_data["y0"] = 0 
        self.entered_data["y2"] = 0 
        self.entered_data["y5"] = 0 
        self.entered_data["y7"] = 0 
        self.entered_data["y8"] = 0 
        self.entered_data["y11"] = 0
        self.entered_data["y12"] = 0 
        self.frames = 0
        self.firstRun = True
        self.text_box, self.name = self.create_styled_textbox(0.07, 0.18, "light green")
        self.popup_btn = self.create_rounded_button("Submit", "light green", self.show_popup, 0.02, 0.3)
        self.inSetup = True
        self.setupRun()

        entry1 = tk.Entry(self.root) 
        # canvas1.create_window(200, 140, window=entry1)
        # data
        # with open("front_data.json", "w") as json_file:
        #     json.dump(data, json_file, indent=4)
        #self.setupRun = False

    def update(self):
        # Capture the video frame by frame
        if self.firstRun:
            for index, record in enumerate(self.loaded_data):
                if record["name"] == str(self.dropdown_var.get()):
                    self.integer = index
                    self.firstRun = False

        # needs to be here cannot be in backend
        if self.is_playing:
            _, img = self.vid.read()
            img = cv2.rotate(img, cv2.ROTATE_180)
            img, self.time, self.i = run(img, self.i, self.detector, self.loaded_data, self.integer, False, timer=self.time, pi_port = self.pi_port)
            opencv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            opencv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            captured_image = Image.fromarray(opencv_image)
            photo_image = ImageTk.PhotoImage(image=captured_image)
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)
            self.label_widget.after(10, self.update)

    def switch_to_front(self):
        self.root.destroy()

        from front.gui import front_gui   # lazy import to avoid circular import
        front_gui()

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


def side_gui(pi_port):
    root = tk.Tk()
    ico = Image.open('duck.png')
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(False, photo)
    root.configure(bg="black")
    root.bind('<Escape>', lambda e: root.quit())
    app = SideGUI(root, pi_port=pi_port)

    root.mainloop()
