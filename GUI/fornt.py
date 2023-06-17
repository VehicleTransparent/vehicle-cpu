from tkinter import *
import tkinter as tk
from tkinter.ttk import *
from PIL import Image, ImageTk


import os

'''
  GUI file to fire front car system 
'''






class Gui:
    def __init__(self,distance=9):
        # create main window and set title,background and size
        self.main_window = tk.Tk()
        self.main_window.title("Front car")
        self.main_window.geometry("1920x1080")
        #self.main_window.configure(background="#73dfed")

        # full screen mode
        #self.main_window.attributes("-fullscreen", True)
        #self.main_window.resizable(0, 0)

        # to hide cursor and bind click event
        #self.main_window.config(cursor="none")
        #self.main_window.bind('<ButtonPress-1>', self.call_back_click_event)


        # create label for page address
        image = ImageTk.PhotoImage(file='photo.png')
        canvas = Canvas(self.main_window, width=1920, height=1080)
        canvas.pack(expand=True, fill=BOTH)
        # Add the image in the canvas
        #canvas.create_image(0, 0, image=image, anchor="nw")



        # configure style for button
        #self.style = Style()
        #self.style.configure('TButton', font=('calibre',34, 'bold'),height=700, width=20,borderwidth='5', background="#AFD1EE",foreground="#2196C1")
        #self.style.map('TButton', foreground=[('active', 'green')],background=[('active', "green")])

        # create label for page address
        self.page_address = Label(font=('vendor', 32, 'bold'), text='XtraVue')
        self.page_address.place(relx=.50, rely=.76, anchor="center")

        self.button = tk.Button(self.main_window, text="Available", command=self.call_back,
                                font=('calibre', 16, 'bold'), bd=0, highlightthickness=0)
        self.button.pack()
        self.button.place(relx=.50, rely=.82, anchor="center")



        self.check_distance(distance);

        self.main_window.mainloop()


    # check distance and blink button if distance is more than 10
    def check_distance(self,dista=0):
        self.distance = dista  # Replace this with your distance calculation logic
        if self.distance < 10:
            self.button.after(500, self.blink_button)    # Blink every 500 milliseconds
        else:
            self.button.after_cancel(self.blink_button)  # cancel blink button
            if self.button is not None:                  #destroy button
                self.button.destroy()
                self.button = None



    # blink button
    def blink_button(self):
        if self.button['foreground'] == 'green':
            self.button['foreground'] = '#000000'
            #self.button['background'] = '#D3D3D3'
        else:
            self.button['foreground'] = 'green'
            #self.button['background'] = '#D3D3D3'
        self.button.after(500, self.blink_button)  # Blink every 500 milliseconds

    # call back function to do action for button
    def call_back(self):
        print("hello world")
        # os.system('python main.py')
        #self.main_window.destroy()


    # call back function to do action for button
    def call_back_click_event(self,event):
        print('hello world')
        page_address = Label(font=('vendor', 28, 'bold'), text='system run', background="#AFD1EE")
        page_address.place(relx=.5, rely=.25, anchor="center")
        # os.system('python main.py')
        # self.main_window.destroy()




gui = Gui()
