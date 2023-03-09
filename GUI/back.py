import threading
import time
from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk
import sys, cv2
from threading import Thread

sys.path.extend(['D:\\GP\\code\\VehiclesTransparent'])
from back_app.main_back import BackMode

'''
  GUI file to fire back car system 
'''


class Gui:
    def __init__(self):
        # create main window and set title and background
        self.main_window = Tk()
        self.main_window.title("Back car")
        self.main_window.geometry("1500x850")
        self.main_window.configure(background="#73dfed")
        self.main_window.attributes("-fullscreen", True)
        self.main_window.resizable(0, 0)
        self.main_window.config(cursor="none")
        self.main_window.bind('<ButtonPress-1>', self.call_back_click_event)

        image = ImageTk.PhotoImage(file='D:\\GP\\code\\VehiclesTransparent\\GUI\\photo.png')
        canvas = Canvas(self.main_window, width=1920, height=1080)
        canvas.pack(expand=True, fill=BOTH)
        # Add the image in the canvas
        canvas.create_image(0, 0, image=image, anchor="nw")

        # create label for page address
        page_address = Label(font=('vendor', 28, 'bold'), text=' V2V Back car ', background="#AFD1EE")
        page_address.place(relx=.5, rely=.02, anchor="center")

        self.connection_status = Label(font=('vendor', 28, 'bold'), text='Request A Connection', background="#AFD1EE")
        self.connection_status.place(relx=.5, rely=.25, anchor="center")
        self.bm = BackMode(ip="192.168.1.11", timeout=4, source="video2.mp4")
        self.main_window.mainloop()

    # call back function to do action for binding on mouse click
    def call_back_click_event(self, event):
        if self.bm.data_sock_receive.connect_mechanism():
            # self.main_window.destroy()
            t_warning = Thread(target=self.update_warning, args=[self.bm.received_fd], daemon=True)
            t_warning.start()
            self.bm(self.main_window.destroy)
            time.sleep(0.5)
            self.__init__()

    def update_warning(self, temp):
        """
        asynchronously update flags in left and right to inform user not to pass
        """
        while True:
            if self.bm.data_sock_receive.connected:
                buffer_disc = temp.get_discrete()
                buffer_frame = temp.get_frame()
                #   [[left_dist, ang], [center_dist, ang], [right_dist, ang]],[length] ]
                print(f"\n\n\nself.bm.received_fd.get_discrete(){self.bm.received_fd.get_discrete()}\n\n\n")

                if buffer_disc is not None:

                    if buffer_disc[0][0][1] < 0:
                        print("Don't Pass left is not Secure")

                    if buffer_disc[0][2][1] < 0:
                        print("Don't Pass right is not Secure")

            time.sleep(0.1)


gui = Gui()
