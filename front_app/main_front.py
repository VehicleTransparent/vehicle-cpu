import time, cv2
from communication.com_socket import *
from threading import Thread
from cv_algorithm.frontal_computer_vision_app import ComputerVisionFrontal
from communication.com_serial import SerialComm


class FrontMode:
    current_v_length = 5

    def __init__(self, ip="127.0.0.1", port=20080, timeout=1, source=0, name="Front Sender"):
        '''
        - Create CV object.
        - run Cv_obj.run_front() in thread.
        - Update frame, discrete from Cv_obj's attributes {frame_to_send}, {angle_to_send}
        - send discrete from Cv_obj's attributes {angle_to_send} to measurement module
        - send frame from Cv_obj's attributes {frame_to_send} to outer machine
        '''
        # instance for run ComputerVisionFrontal class
        self.ip, self.port, self.timeout, self.name = ip, port, timeout, name
        self.data_sock_send = Server(ip=self.ip, port=self.port, timeout=self.timeout, name=self.name)
        self.ser_get_distance = SerialComm(port="COM11", name="Receiver", baudrate=115200)

        self.source = source
        self.to_send_fd = DataHolder()

        self.computer_vision_frontal_instance = ComputerVisionFrontal(source=self.source)
        # CV model run front in thread
        # self.t_cv_front = ComputerVisionFrontal()

        self.dist_list = [0] * 3
        self.cv_angle_list = self.last_angle_values = [0] * 3
        self.threads_activated = False

    def __call__(self, call_back):
        call_back()

        self.computer_vision_frontal_instance.run_front(self.data_sock_send)


    def update_all(self, send_fd, data_sock):
        while self.data_sock_send.connect_mechanism():
            to_send = {"F": send_fd.get_frame(),
                       "D": 1}
            data_sock.send_all(to_send)





    def distance_fetcher(self):
        while True:
            received = self.ser_get_distance.receive_query()
            if received:
                self.dist_list = received["DISTANCE"]

