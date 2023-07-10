import threading

import cv2
import tkinter as tk
from PIL import Image, ImageTk
import screeninfo

from back_app.main_back import BackMode
from communication.com_socket import DataHolder


def get_screen_resolution():
    screen_info = screeninfo.get_monitors()[0]
    resolution = (screen_info.width, screen_info.height)
    return resolution


class BackVehicleGUIApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Back Vehicle Application")
        self.window.geometry("1280x720")

        self.bm = BackMode(gui=self, ip="127.0.0.1", timeout=4, source="..\\gui\\rear_HQ.mp4")

        self.screen_width, self.screen_height = get_screen_resolution()

        self.window_width = 1280
        self.window_height = 720

        self.main_video_width = 750
        self.main_video_height = 525

        self.side_video_width = 400
        self.side_video_height = 300

        self.main_video_holder = DataHolder()
        self.side_video1_holder = DataHolder()
        self.side_video2_holder = DataHolder()

        self.main_frame = tk.Frame(self.window)
        self.main_frame.grid(row=0, column=0, padx=40, pady=0, rowspan=2)

        self.side_frame1 = tk.Frame(self.window)
        self.side_frame1.grid(row=0, column=1, padx=20, pady=0, sticky=tk.NE)

        self.side_frame2 = tk.Frame(self.window)
        self.side_frame2.grid(row=1, column=1, padx=20, pady=10, sticky=tk.NE)

        self.main_canvas = tk.Canvas(self.main_frame, width=self.main_video_width, height=self.main_video_height,
                                     highlightthickness=1, highlightbackground="black")
        self.main_canvas.pack()

        self.side_canvas1 = tk.Canvas(self.side_frame1, width=self.side_video_width, height=self.side_video_height,
                                      highlightthickness=1, highlightbackground="black")
        self.side_canvas1.pack()

        self.side_canvas2 = tk.Canvas(self.side_frame2, width=self.side_video_width, height=self.side_video_height,
                                      highlightthickness=1, highlightbackground="black")
        self.side_canvas2.pack()

        self.label_main = tk.Label(self.main_frame, text="Screen")
        self.label_main.pack(pady=0)

        self.label_side1 = tk.Label(self.side_frame1, text="Camera")
        self.label_side1.pack(pady=0)

        self.label_side2 = tk.Label(self.side_frame2, text="Incoming Stream")
        self.label_side2.pack(pady=0)

        self.thread_activated = False


    def update_main_frame(self, frame):
        frame_main = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_main_resized = cv2.resize(frame_main, (self.main_video_width, self.main_video_height))
        image_main = Image.fromarray(frame_main_resized)
        photo_main = ImageTk.PhotoImage(image_main)
        self.main_canvas.create_image(0, 0, image=photo_main, anchor=tk.NW)
        self.main_canvas.image = photo_main

    def update_side_frame1(self, frame):
        frame_side1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_side1_resized = cv2.resize(frame_side1, (self.side_video_width, self.side_video_height))
        image_side1 = Image.fromarray(frame_side1_resized)
        photo_side1 = ImageTk.PhotoImage(image_side1)
        self.side_canvas1.create_image(0, 0, image=photo_side1, anchor=tk.NW)
        self.side_canvas1.image = photo_side1

    def update_side_frame2(self, frame):
        frame_side2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_side2_resized = cv2.resize(frame_side2, (self.side_video_width, self.side_video_height))
        image_side2 = Image.fromarray(frame_side2_resized)
        photo_side2 = ImageTk.PhotoImage(image_side2)
        self.side_canvas2.create_image(0, 0, image=photo_side2, anchor=tk.NW)
        self.side_canvas2.image = photo_side2


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
            self.side_frame1.grid_remove()
            self.side_frame2.grid_remove()
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
            self.side_frame1.grid()
            self.side_frame2.grid()

    def update_frames(self):
        frame_main = self.main_video_holder.get_frame()
        frame_side1 = self.side_video1_holder.get_frame()
        frame_side2 = self.side_video2_holder.get_frame()

        if frame_main is not None:
            self.update_main_frame(frame_main)

        if frame_side1 is not None:
            self.update_side_frame1(frame_side1)

        if frame_side2 is not None:
            self.update_side_frame2(frame_side2)

        self.window.after(10, self.update_frames)

    def connect(self):
        while not self.bm.data_sock_receive.connected:
            self.bm.data_sock_receive.connect_mechanism()
        if not self.thread_activated:
            bm_thread = threading.Thread(target=self.bm, args=[], daemon=False)
            bm_thread.start()
            self.thread_activated = True


    def run(self):
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=2, column=0, padx=40, pady=10)

        fullscreen_button = tk.Button(button_frame, text="Full Screen", command=self.toggle_fullscreen)
        fullscreen_button.pack(side=tk.LEFT)

        connect_button = tk.Button(button_frame, text="Connect", command=self.connect)
        connect_button.pack(side=tk.LEFT, padx=10)

        self.update_frames()
        self.window.mainloop()



app = BackVehicleGUIApp(tk.Tk())
app.run()
