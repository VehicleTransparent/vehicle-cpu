import sys

import screeninfo
import torch

from communication.com_serial import *
from communication.com_socket import *
from mathematics.services import calculate_rectangle_center, calculate_area, map_values_ranges

"""
    1. Naming.
    2. each function does only one job.
    3. function length <= 10 lines.
"""





class MultiCarsDetection:
    PREDICTION_THRESHOLD = 0.75
    CAR = 2
    BUS = 5
    TRUCK = 7
    TOP_LEFT_X = 'xmin'
    TOP_LEFT_Y = 'ymin'
    BOTTOM_RIGHT_X = 'xmax'
    BOTTOM_RIGHT_Y = 'ymax'

    def __init__(self, width, height, conf_threshold=0.2):
        self.result = None
        self.detected_vehicles_data_frame = None
        print("Loading Object Detection")
        print("Running YOLOv5n")
        self.model = torch.hub.load('ultralytics/yolov5', 'custom',
                                    path='..\\cv_algorithm\\best.pt')  # Load custom YOLOv5 model
        self.conf_threshold = conf_threshold  # Reject any predictions with confidence less than threshold
        self.model.classes_to_detect = [MultiCarsDetection.CAR, MultiCarsDetection.BUS, MultiCarsDetection.TRUCK]

        self.width = width
        self.height = height

        self.end_left_section = round(width * (3 / 8))
        self.end_middle_section = round(width * (6 / 8))
        self.end_right_section = width

    def detect(self, frame):
        """return list of the closest vehicle area for each section, 0 left, 1 middle, 2 right"""
        self.result = self.model(frame)

        self.detected_vehicles_data_frame = self.result.pandas().xyxy[0]

        # Delete detected vehicles which is under-prediction threshold
        self.detected_vehicles_data_frame = \
            self.detected_vehicles_data_frame[self.detected_vehicles_data_frame['confidence'] > self.conf_threshold]

        if not self.detected_vehicles_data_frame.empty:
            self.add_vehicles_areas_to_data_frame()
            # LEFT CAR BOUNDING BOX
            left_section_vehicles = self.detected_vehicles_data_frame[
                self.detected_vehicles_data_frame[MultiCarsDetection.BOTTOM_RIGHT_X] <= self.end_left_section]
            middle_section_vehicles = self.detected_vehicles_data_frame[
                (self.detected_vehicles_data_frame[MultiCarsDetection.BOTTOM_RIGHT_X] > self.end_left_section) &
                (self.detected_vehicles_data_frame[MultiCarsDetection.BOTTOM_RIGHT_X] <= self.end_middle_section)]
            right_section_vehicles = self.detected_vehicles_data_frame[
                (self.detected_vehicles_data_frame[MultiCarsDetection.BOTTOM_RIGHT_X] > self.end_middle_section) &
                (self.detected_vehicles_data_frame[MultiCarsDetection.BOTTOM_RIGHT_X] <= self.end_right_section)]

            left_section_car_center = self.get_and_draw_closest_detected_vehicle_box_and_center(
                frame, left_section_vehicles, (0, 0, 255))
            middle_section_car_center = self.get_and_draw_closest_detected_vehicle_box_and_center(
                frame, middle_section_vehicles, (0, 255, 0))
            right_section_car_center = self.get_and_draw_closest_detected_vehicle_box_and_center(
                frame, right_section_vehicles, (255, 0, 0))

            cars_sections = [left_section_car_center, middle_section_car_center,
                             right_section_car_center]
            return cars_sections  # return list of the closest vehicle area for each section, 0 left, 1 middle, 2 right
        else:
            return [(-1, 0), (-1, 0), (-1, 0)]

    def get_and_draw_closest_detected_vehicle_box_and_center(self, frame, section_vehicles, section_color=(0, 0, 255)):
        if not section_vehicles.empty:
            # GET CENTER
            left_section_closest_vehicle = self.detected_vehicles_data_frame.iloc[
                section_vehicles['area'].idxmax()]

            left_section_car_center = calculate_rectangle_center(
                left_section_closest_vehicle[MultiCarsDetection.TOP_LEFT_X],
                left_section_closest_vehicle[MultiCarsDetection.TOP_LEFT_Y],
                left_section_closest_vehicle[MultiCarsDetection.BOTTOM_RIGHT_X],
                left_section_closest_vehicle[MultiCarsDetection.BOTTOM_RIGHT_Y])

            top_left_corner = (round(left_section_closest_vehicle[MultiCarsDetection.TOP_LEFT_X]),
                               round(left_section_closest_vehicle[MultiCarsDetection.TOP_LEFT_Y]))

            bottom_right_corner = (round(left_section_closest_vehicle[MultiCarsDetection.BOTTOM_RIGHT_X]),
                                   round(left_section_closest_vehicle[MultiCarsDetection.BOTTOM_RIGHT_Y]))
            # # DISPLAY BOUNDING BOX
            # cv2.rectangle(frame, top_left_corner, bottom_right_corner, color=section_color, thickness=2)
            # # DISPLAY CENTER DOT
            # cv2.circle(frame, left_section_car_center, radius=1, color=section_color, thickness=2)

        else:
            left_section_closest_vehicle = 0
            left_section_car_center = (-1, 0)
        return left_section_car_center

    def add_vehicles_areas_to_data_frame(self):
        self.detected_vehicles_data_frame['area'] = self.detected_vehicles_data_frame.apply(
            lambda x: calculate_area(x[MultiCarsDetection.TOP_LEFT_X],
                                     x[MultiCarsDetection.TOP_LEFT_Y],
                                     x[MultiCarsDetection.BOTTOM_RIGHT_X],
                                     x[MultiCarsDetection.BOTTOM_RIGHT_Y]), axis=1
        )


class ComputerVisionFrontal:
    IN_MIN = 0
    IN_MAX = 180
    OUT_MIN = 0
    OUT_MAX = 14

    def __init__(self, source=0, to_send_fd=None):
        self.screen = screeninfo.get_monitors()[0]
        self.width, self.height = self.screen.width, self.screen.height
        # Some Initial  Parameters
        # Detection Instances
        self.od = MultiCarsDetection(width=self.width, height=self.height)
        self.ser_object = SerialComm(port="COM9", name="Receiver", baudrate=115200)
        self.angle_map = {"DISTANCE": [-1] * 15}
        self.angle_to_send = None
        self.dist_list = [0] * 3
        self.to_send_fd = to_send_fd
        self.source = source
        self.video = cv2.VideoCapture(self.source)  # CAMERA - RECORDED VIDEO - SIMULATION
        # Read video

    def run_front(self, sock, frames_per_detect=10, current_v_length=5):
        frames_counter = 0
        disc = None
        first_frame = True

        # Exit if video not opened.
        while not self.video.isOpened():
            print("Could not open video")
            self.video = cv2.VideoCapture(self.source)  # CAMERA - RECORDED VIDEO - SIMULATION
            self.angle_to_send = [(-1, 0), (-1, 0), (-1, 0)]

            # sys.exit()

        while True:
            # Read Frame by frame
            ok, frame = self.video.read()

            # while frame is None:
            #     cv2.VideoCapture(self.source)

            # Exit if video not opened.
            if not ok:
                print('Cannot read video file')
                self.angle_to_send = [-1, -1, -1]
                sys.exit()

            frame = cv2.resize(frame, (self.width, self.height))  # Resize the Frame
            if frames_counter >= frames_per_detect or first_frame:
                self.cars_sections = self.od.detect(frame=frame)
                frames_counter = 0
                first_frame = False

            frames_counter += 1

            self.angle_to_send = [
                map_values_ranges(input_value=c[0], input_range_min=0, input_range_max=self.width,
                                  output_range_min=0, output_range_max=180) for c in self.cars_sections]
            if self.ser_object:
                self.angle_map = self.ser_object.receive_query()
            else:
                self.ser_object = SerialComm(port="COM9", name="Receiver", baudrate=115200)
            if self.angle_map is not None and type(self.angle_map) is dict:
                # Angels extract from map
                self.dist_list = [round(map_values_ranges(self.angle_map['DISTANCE'][i],
                                                          ComputerVisionFrontal.IN_MIN,
                                                          ComputerVisionFrontal.IN_MAX,
                                                          ComputerVisionFrontal.OUT_MIN,
                                                          ComputerVisionFrontal.OUT_MAX))
                                  for i in range(0, 3)]

                disc = [[[self.dist_list[i], self.angle_to_send[i]] for i in range(0, 3)], current_v_length]
            self.to_send_fd.set_frame(frame)
            self.to_send_fd.set_discrete(disc)

            # Showing The Video Frame
            window_name = 'Current Front'
            cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.moveWindow(window_name, self.screen.x - 1, self.screen.y - 1)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                                  cv2.WINDOW_FULLSCREEN)
            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # if press q
                self.angle_to_send = [(-1, 0), (-1, 0), (-1, 0)]
                # sys.exit()
                break

        self.video.release()
        cv2.destroyAllWindows()
