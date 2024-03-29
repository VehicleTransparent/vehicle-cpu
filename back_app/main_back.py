from threading import Thread
import time, cv2
from communication.com_socket import *
from cv_algorithm.back_computer_vision_app import ComputerVisionBackApp
from communication.com_serial import SerialComm
from mathematics.mathlib import *


class BackMode:
    def __init__(self, gui, ip="127.0.0.1", port=20070, timeout=1, source=0, name="Receive Socket"):
        '''
        - Create CV object.
        - Create one measurement unit.
        - run Cv_obj.run_back() in thread.
        - receive frame, discrete from Cv_obj's sockets (applied internally in CV_back_app)
        - read single distance
        - pass all parameters to mathematical model
        '''
        self.gui = gui
        self.ip, self.port, self.timeout, self.name, self.source = ip, port, timeout, name, source
        self.data_sock_receive = Client(ip=self.ip, port=self.port, timeout=self.timeout, name=self.name)
        self.ser_get_distance = SerialComm(port="COM10", name="Receiver", baudrate=115200)

        # instance for run ComputerVisionFrontal class
        self.computer_vision_back_instance = None
        self.received_frame = None
        self.received_discrete = None
        self.direct_distance = None
        self.dist_list = None

        self.computer_vision_back_instance = ComputerVisionBackApp(source=self.source)

        # CV model run front in thread
        self.t_cv_back = Thread(target=self.computer_vision_back_instance.run_back,
                                args=[self.data_sock_receive, self.gui], daemon=False)
        self.t_get_dist_asynch = Thread(target=self.distance_fetcher, args=[], daemon=False)

        self.threads_activated = False

    def __call__(self):

        while self.data_sock_receive.connected:
            if not self.threads_activated:
                self.threads_activated = True
                self.t_cv_back.start()
                # self.t_get_dist_asynch.start()



            received_frame, received_discrete = self.data_sock_receive.receive_all(1024)
            # cv2.imshow("Informed Frame", frame)
            if received_frame is not None:
                self.gui.side_video2_holder.set_frame(received_frame)
                self.computer_vision_back_instance.data_holder.set_frame(received_frame)

            if received_discrete is not None and type(self.computer_vision_back_instance.front_vehicle_center) is list:
                # Update frames which is received from socket.
                self.computer_vision_back_instance.data_holder.set_discrete(received_discrete)
                angles = [-1, self.computer_vision_back_instance.front_vehicle_center[0], -1]
                self.ser_get_distance.send_query({"ORIENT": angles})

                if self.direct_distance is not None:
                    abs_dist = math_model(data=received_discrete[0],
                                          vehicle_length=received_discrete[1],
                                          direct_distance=self.direct_distance,
                                          theta=self.computer_vision_back_instance.front_vehicle_center[0])

                    print(f"Front Vehicle Center: {self.computer_vision_back_instance.front_vehicle_center[0]}")
                    print(f"Absolute Distances: {abs_dist}")

            print(f'Direct Distance: \n{self.direct_distance}')

        self.data_sock_receive.s.close()

    def distance_fetcher(self):
        while self.data_sock_receive.connected:
            received = self.ser_get_distance.receive_query()
            if received:
                self.dist_list = received["DISTANCE"]

