import threading

import cv2
import tkinter as tk

import screeninfo
from PIL import Image, ImageTk

from communication.com_socket import DataHolder
from front_app.main_front import FrontMode

def get_screen_resolution():
    screen_info = screeninfo.get_monitors()[0]
    resolution = (screen_info.width, screen_info.height)
    return resolution


class FrontVehicleGUIApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Front Vehicle Application")
        self.window.geometry("1280x720")

        self.screen_width, self.screen_height = get_screen_resolution()

        self.main_video_width = 750
        self.main_video_height = 525

        self.side_video_width = 400
        self.side_video_height = 300

        self.fm = FrontMode(gui=self, ip="127.0.0.1", timeout=3, source="..\\gui\\front_HQ.mp4")

        self.main_video_holder = DataHolder()
        self.side_video_holder = DataHolder()

        self.main_frame = tk.Frame(self.window)
        self.main_frame.grid(row=0, column=0, padx=40, pady=0)

        self.side_frame = tk.Frame(self.window)
        self.side_frame.grid(row=0, column=1, padx=20, pady=0, sticky=tk.NE)

        self.main_canvas = tk.Canvas(self.main_frame, width=self.main_video_width, height=self.main_video_height,
                                     highlightthickness=1, highlightbackground="black")
        self.main_canvas.pack()

        self.side_canvas = tk.Canvas(self.side_frame, width=self.side_video_width, height=self.side_video_height,
                                      highlightthickness=1, highlightbackground="black")
        self.side_canvas.pack()

        self.label_main = tk.Label(self.main_frame, text="Screen")
        self.label_main.pack(pady=10)

        self.label_side = tk.Label(self.side_frame, text="Sending Frame")
        self.label_side.pack(pady=10)

        self.button_frame = tk.Frame(self.window)
        self.button_frame.grid(row=2, column=0, padx=40, pady=10)

        self.fullscreen_button = tk.Button(self.button_frame, text="Full Screen", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(side=tk.LEFT)

        self.label_connection = tk.Label(self.button_frame, text="Connection Status: Idle")
        self.label_connection.pack(side=tk.LEFT, padx=10)

        self.thread_activated = False

        self.start_connection()

        self.update_frames()

    def start_connection(self):
        if not self.thread_activated:
            fm_thread = threading.Thread(target=self.fm, args=[], daemon=False)
            fm_thread.start()
            self.thread_activated = True


    def update_main_frame(self, frame):
        frame_main = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_main_resized = cv2.resize(frame_main, (self.main_video_width, self.main_video_height))
        image_main = Image.fromarray(frame_main_resized)
        photo_main = ImageTk.PhotoImage(image_main)
        self.main_canvas.create_image(0, 0, image=photo_main, anchor=tk.NW)
        self.main_canvas.image = photo_main

    def update_side_frame(self, frame):
        frame_side = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_side_resized = cv2.resize(frame_side, (self.side_video_width, self.side_video_height))
        image_side = Image.fromarray(frame_side_resized)
        photo_side = ImageTk.PhotoImage(image_side)
        self.side_canvas.create_image(0, 0, image=photo_side, anchor=tk.NW)
        self.side_canvas.image = photo_side

    def update_frames(self):
        frame_main = self.main_video_holder.get_frame()
        frame_side = self.side_video_holder.get_frame()

        if frame_main is not None:
            self.update_main_frame(frame_main)

        if frame_side is not None:
            self.update_side_frame(frame_side)

        self.window.after(10, self.update_frames)

    def toggle_fullscreen(self):
        if not self.window.attributes("-fullscreen"):
            self.window.attributes("-fullscreen", True)
            self.window.overrideredirect(True)
            self.window.geometry(f"{self.screen_width}x{self.screen_height}")
            self.window.grid_rowconfigure(0, weight=1)
            self.window.grid_columnconfigure(0, weight=1)
            self.main_frame.grid(row=0, column=0, padx=0, pady=0, rowspan=2, sticky="nsew")
            self.main_video_width = self.screen_width
            self.main_video_height = self.screen_height
            self.main_frame.configure(width=self.screen_width, height=self.screen_height)
            self.main_canvas.configure(width=self.screen_width, height=self.screen_height)
            self.side_frame.grid_remove()
        else:
            self.main_video_width = 750
            self.main_video_height = 525
            self.window.attributes("-fullscreen", False)
            self.window.overrideredirect(False)
            self.window.geometry("1280x720")
            self.window.grid_rowconfigure(0, weight=0)
            self.window.grid_columnconfigure(0, weight=0)
            self.main_frame.grid(row=0, column=0, padx=40, pady=0, rowspan=2)
            self.main_frame.configure(width=self.main_video_width, height=self.main_video_height)
            self.main_canvas.configure(width=self.main_video_width, height=self.main_video_height)
            self.side_frame.grid()


app = FrontVehicleGUIApp(tk.Tk())
app.window.mainloop()
