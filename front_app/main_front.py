
import time
import cv2

# uncomment to test on RPi
# from distances.dist_measure import *
# from distances.dist_angle import *

# uncomment this to test on PC
from Tools.Test_Measure_app_Front import *
from comlib.com_socket import *
from threading import Thread
from cv_algorithm.frontal_computer_vision_app import ComputerVisionFrontal


class FrontMode:
    current_v_length = 5
    def __init__(self, ip="127.0.0.1", port=20070, timeout=1, name="Front Sender"):
        '''
        - Create CV object.
        - run Cv_obj.run_front() in thread.
        - Update frame, discrete from Cv_obj's attributes {frame_to_send}, {angle_to_send}
        - send discrete from Cv_obj's attributes {angle_to_send} to measurement module
        - send frame from Cv_obj's attributes {frame_to_send} to outer machine
        '''
        # instance for run ComputerVisionFrontal class
        self.ip, self.port, self.timeout, self.name = ip, port, timeout, name
        self.out_sock_frame = Server(ip=self.ip, port=self.port, timeout=self.timeout, name=self.name)
        self.to_send_fd = DataHolder()
        self.computer_vision_frontal_instance = ComputerVisionFrontal()
        # CV model run front in thread
        self.t_cv_front = Thread(target=self.computer_vision_frontal_instance.run_front, args=[], daemon=True)
        self.t_update_f = Thread(target=self.update_all, args=[self.to_send_fd, self.out_sock_frame], daemon=True)
        self.t_update_f.start()
        self.servo_obj_list = [Angles(servo_pin=11), Angles(servo_pin=12), Angles(servo_pin=13)]
        self.us_obj_list = [Measure(trig=22, echo=23), Measure(trig=24, echo=25), Measure(trig=26, echo=27)]
        self.dist_list = [0] * 3
        self.cv_angle_list = self.last_angle_values = [0] * 3
        self.t_cv_front.start()

    def __call__(self):
        while True:
            self.cv_angle_list = self.computer_vision_frontal_instance.angle_to_send
            if self.computer_vision_frontal_instance.angle_to_send is None:
                cv_angle_list = [45, 90, 135]

            # Check if the last received values is different
            for section in range(0, len(self.servo_obj_list)):
                self.servo_obj_list[section].set_angle(cv_angle_list[section])
                self.dist_list[section] = self.us_obj_list[section].distance_read()

            disc = [[[self.dist_list[i], cv_angle_list[i]] for i in range(0, 3)], FrontMode.current_v_length]
            self.to_send_fd.set_discrete(disc)
            self.to_send_fd.set_frame(self.computer_vision_frontal_instance.frame_to_send)

            print(f'APP: to send: {self.to_send_fd.get_discrete()}')
            time.sleep(0.02)

    def update_all(self, send_fd, data_sock):
        while True:
            to_send = {"F": send_fd.get_frame(),
                       "D": send_fd.get_discrete()}
            data_sock.send_all(to_send)
            if to_send["F"] is not None:
                cv2.imshow('SOCK_Sending This Frame...', to_send["F"])
            time.sleep(0.01)
