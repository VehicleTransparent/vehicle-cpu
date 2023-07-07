import math
import sys
import time

import cv2
import screeninfo
import torch
import numpy as np
from communication.com_socket import DataHolder


# Object Detection Class


class SingleCardDetection:
    DEF_VAL = 0
    DEF_FLOAT = 0.0
    DEF_TXT = ''
    CONFIDENCE_THRESHOLD = 0.6

    def __init__(self, conf_threshold=0.2, area_threshold=13000):
        self.screen = screeninfo.get_monitors()[0]
        self.width, self.height = self.screen.width, self.screen.height
        print("Loading Object Detection")
        print("Running custom YOLOv5 model")
        self.model = torch.hub.load('ultralytics/yolov5', 'custom',
                                    path='..\\cv_algorithm\\best.pt')  # Load custom YOLOv5 model
        self.conf_threshold = conf_threshold  # Reject any predictions with confidence less than threshold
        self.area_threshold = area_threshold

    def calc_area_and_center(self, x_min, y_min, x_max, y_max):
        # Calculate the area of the bounding box
        area = (x_max - x_min) * (y_max - y_min)
        # Calculate the center coordinates of the bounding box
        center_x = x_min + ((x_max - x_min) // 2)
        center_y = y_min + ((y_max - y_min) // 2)
        return int(area), (int(center_x), int(center_y))

    def distance(self, point1, point2):
        # Calculate Euclidean distance between two points
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def detect(self, frame, roi_center):
        self.x1, self.y1, self.x2, self.y2, self.text, self.conf, self.area = SingleCardDetection.DEF_VAL, \
                                                                              SingleCardDetection.DEF_VAL, \
                                                                              SingleCardDetection.DEF_VAL, \
                                                                              SingleCardDetection.DEF_VAL, \
                                                                              SingleCardDetection.DEF_TXT, \
                                                                              SingleCardDetection.DEF_FLOAT, \
                                                                              SingleCardDetection.DEF_VAL
        self.result = self.model(frame)
        self.df = self.result.pandas().xyxy[0]
        self.df = self.df[self.df['confidence'] > self.conf_threshold]

        if not self.df.empty:
            self.df['area'], self.df['center'] = zip(
                *self.df.apply(lambda x: self.calc_area_and_center(x['xmin'], x['ymin'], x['xmax'], x['ymax']), axis=1))
            self.df = self.df[self.df['area'] > self.area_threshold]  # Filter out areas less than 13000
            if not self.df.empty:
                self.df['distance_to_roi'] = self.df['center'].apply(
                    lambda x: self.distance(roi_center, x))  # Calculate distance from roi_center to car centers
                nearest_car = self.df[self.df['distance_to_roi'] == self.df['distance_to_roi'].min()].iloc[
                    0]
                # Get nearest car
                self.x1, self.y1 = int(nearest_car['xmin']), int(nearest_car['ymin'])
                self.x2, self.y2 = int(nearest_car['xmax']), int(nearest_car['ymax'])
                self.label = nearest_car['name']
                self.conf = nearest_car['confidence']
                self.text = f"{self.label}, {self.conf:.2f}"
                self.area = nearest_car['area']
        return self.x1, self.y1, self.x2, self.y2, self.text, self.conf, self.area  #


'''
# Note for applying the depth over the filling video:
* In the run function we have [streamedData,and detected_car_width, detected_car_height ] before add_weight function
* We will apply masking over that image 'streamedData' according to these resolutions detected_car_width, detected_car_height.
* We have the frontal car length [for testing purposes we assume it will be fixed with 3m].
* By using the frontal car length as a zoom-out factor, we should map this length with a ratio ranging between zero and one.
* The normal length range of normal vehicles is between 3m to 13m, so the ratio will be between 0.0 and 1.0 with step 0.1, in reverse order.
* 0.1 per 1 m, since we fixed the length by 3 m, the ratio will be 0.1
* As 0.1 is the reduced ratio, the zoom_out factor will be 1 - 0.1  = 0.9
'''


class ComputerVisionBackApp:
    width_ratio = 0.15
    height_ratio = 0.3

    def __init__(self, source=0):
        self.screen = screeninfo.get_monitors()[0]
        self.width, self.height = self.screen.width, self.screen.height
        self.C_X, self.C_Y, = int(self.width / 2), int(self.height / 2)
        self.area_threshold = (self.width * self.height) / 55
        self.zoom_factor = 0.9  # Zoom factor (0.6 zooms out by 60%)  For applying depth over the filling video

        # ReSize the Frame
        self.source = source
        # Initialize The x1,y1,x2,y2,text,conf,bbox
        self.x1, self.y1, self.x2, self.y2, self.text, self.conf, self.area, self.bbox, self.fps = 0, 0, 0, 0, '', 0, 0, 0, 0

        # TO_DO: Valeo Icon/Logo as a default pic.
        self.last_streamed_frame = None
        self.last_disc = None
        self.data_holder = DataHolder()
        self.od = SingleCardDetection()
        # Read video (emulates Camera)
        self.video = cv2.VideoCapture(self.source)
        self.logo = cv2.imread('..\\gui\\Valeo.png')
        self.front_vehicle_center = self.width // 2
        self.data_holder.reset_discrete()

    def video_filling_coordinates(self, x1, y1, x2, y2, detected_car_width, detected_car_height):
        new_detected_car_width = round(detected_car_width * 0.9)
        new_detected_car_height = round(detected_car_height * 0.33)
        x1 = round(x1 + detected_car_width * 0.05)
        y1 = round(y1 + detected_car_height * 0.3)
        x2 = round(x2 - detected_car_width * 0.05)
        y2 = round(y2 - detected_car_height * 0.3)
        return x1, y1, x2, y2, new_detected_car_width, new_detected_car_height

    def run_back(self, sock):

        self.sock = sock

        # Exit if video not opened.
        while not self.video.isOpened():
            print("Could not open video")
            time.sleep(1)
            sys.exit()
        # print('############# Before Connection Start')
        while sock.connect_mechanism():
            # print('############# After Connection Start')
            # read Frame by frame
            ok, cam_captured_frame = self.video.read()

            # Exit if video not opened.
            if not ok:
                print('Cannot read video file')
                sys.exit()
            # print('############# Video Is Ok')
            timer = cv2.getTickCount()  # Start timer To Calculate FPS
            # Resize the Frame
            cam_captured_frame = cv2.resize(cam_captured_frame, (self.width, self.height))

            roi_center = (self.C_X, (self.C_Y + (self.C_Y // 2)))
            self.x1, self.y1, self.x2, self.y2, self.text, self.conf, self.area = self.od.detect(
                frame=cam_captured_frame, roi_center=(self.C_X, self.C_Y))

            detected_car_width = round(abs(self.x2 - self.x1))
            detected_car_height = round(abs(self.y2 - self.y1))
            self.x1, self.y1, self.x2, self.y2, detected_car_width, detected_car_height = self.video_filling_coordinates(
                self.x1, self.y1, self.x2, self.y2,
                detected_car_width,
                detected_car_height)
            detected_car_width = round(abs(self.x2 - self.x1))
            detected_car_height = round(abs(self.y2 - self.y1))
            # print('############# After Detection ')
            # print('############# Area : ', self.area)
            if self.area != 0:
                try:
                    self.last_streamed_frame, received_discrete = self.sock.receive_all(4)

                    #   self.last_disc = self.data_holder.get_discrete()
                    self.last_streamed_frame = cv2.resize(self.last_streamed_frame,
                                                          (detected_car_width, detected_car_height))
                    # ------------------------------------------------
                    # here we has [streamedData,and detected_car_width, detected_car_height ]
                    # Calculate the new dimensions
                    new_width = int(self.last_streamed_frame.shape[1] / self.zoom_factor)
                    new_height = int(self.last_streamed_frame.shape[0] / self.zoom_factor)

                    # Create a larger canvas
                    zoomed_out_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)

                    # Calculate the position to place the original image on the canvas
                    x = (new_width - self.last_streamed_frame.shape[1]) // 2
                    y = (new_height - self.last_streamed_frame.shape[0]) // 2

                    # Place the original image on the canvas
                    zoomed_out_image[y:y + self.last_streamed_frame.shape[0],
                    x:x + self.last_streamed_frame.shape[1]] = self.last_streamed_frame
                    zoomed_out_image = cv2.resize(zoomed_out_image, (detected_car_width, detected_car_height))
                    # ------------------------------------------------

                    cam_captured_frame[self.y1: self.y2, self.x1: self.x2] = cv2.addWeighted(
                        cam_captured_frame[self.y1: self.y2, self.x1: self.x2], 0.2, zoomed_out_image, 0.8, 0)
                    cam_captured_frame = self.update_warning(cam_captured_frame, self.last_disc)

                    cv2.rectangle(cam_captured_frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 255), 1)
                    self.x1, self.y1, self.x2, self.y2, self.text, self.area = 0, 0, 0, 0, '', 0
                    # Showing The Video Frame
                    window_name = 'Back View'
                    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
                    cv2.moveWindow(window_name, self.screen.x - 1, self.screen.y - 1)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                                          cv2.WINDOW_FULLSCREEN)
                    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);  # Calculate Frames per second (FPS)
                    # Display FPS on frame
                    cv2.putText(cam_captured_frame, "FPS : " + str(int(fps)), (23, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                                (50, 255, 255), 2);

                    cv2.imshow(window_name, cam_captured_frame)

                except:
                    pass


            if cv2.waitKey(1) & 0xFF == ord('q'):
                # sys.exit()
                break


        self.video.release()
        cv2.destroyAllWindows()

    def update_warning(self, frame, disc):
        """
        asynchronously update flags in left and right to inform user not to pass
        """
        secure = [True, True]
        # while True:

        #   [ [[left_dist, ang], [center_dist, ang], [right_dist, ang]],length ]
        print(f"\n\n\nself.bm.received_fd.get_discrete(){disc}\n\n\n")

        if disc is not None:
            if disc[0][0][1] > 0:
                s_img = cv2.imread("..\\gui\\unsafe_left.png", -1)
                y_offset = self.height * 3 // 4
                x_offset = self.width // 4
                y1, y2 = y_offset, y_offset + s_img.shape[0]
                x1, x2 = x_offset - s_img.shape[1], x_offset

                alpha_s = s_img[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s
                frame[y1:y2, x1:x2, 0] = (alpha_s * s_img[:, :, 0] + alpha_l * frame[y1:y2, x1:x2, 0])
                frame[y1:y2, x1:x2, 1] = (alpha_s * s_img[:, :, 1] + alpha_l * frame[y1:y2, x1:x2, 1])
                frame[y1:y2, x1:x2, 2] = (alpha_s * s_img[:, :, 2] + alpha_l * frame[y1:y2, x1:x2, 2])
                print("Don't Pass left is not Secure")

            elif disc[0][0][1] < 0:
                s_img = cv2.imread("..\\gui\\safe_left.png", -1)
                y_offset = self.height * 3 // 4
                x_offset = self.width // 4
                y1, y2 = y_offset, y_offset + s_img.shape[0]
                x1, x2 = x_offset - s_img.shape[1], x_offset

                alpha_s = s_img[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s
                frame[y1:y2, x1:x2, 0] = (alpha_s * s_img[:, :, 0] + alpha_l * frame[y1:y2, x1:x2, 0])
                frame[y1:y2, x1:x2, 1] = (alpha_s * s_img[:, :, 1] + alpha_l * frame[y1:y2, x1:x2, 1])
                frame[y1:y2, x1:x2, 2] = (alpha_s * s_img[:, :, 2] + alpha_l * frame[y1:y2, x1:x2, 2])
                print("Pass left is Secure")

            if disc[0][2][1] > 0:
                s_img = cv2.imread("..\\gui\\unsafe_right.png", -1)
                y_offset = self.height * 3 // 4
                x_offset = self.width * 3 // 4
                y1, y2 = y_offset, y_offset + s_img.shape[0]
                x1, x2 = x_offset, x_offset + s_img.shape[1]

                alpha_s = s_img[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s
                frame[y1:y2, x1:x2, 0] = (alpha_s * s_img[:, :, 0] + alpha_l * frame[y1:y2, x1:x2, 0])
                frame[y1:y2, x1:x2, 1] = (alpha_s * s_img[:, :, 1] + alpha_l * frame[y1:y2, x1:x2, 1])
                frame[y1:y2, x1:x2, 2] = (alpha_s * s_img[:, :, 2] + alpha_l * frame[y1:y2, x1:x2, 2])
                print("Don't Pass right is not Secure")

            elif disc[0][2][1] < 0:
                s_img = cv2.imread("..\\gui\\safe_right.png", -1)
                y_offset = self.height * 3 // 4
                x_offset = self.width * 3 // 4
                y1, y2 = y_offset, y_offset + s_img.shape[0]
                x1, x2 = x_offset, x_offset + s_img.shape[1]

                alpha_s = s_img[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s
                frame[y1:y2, x1:x2, 0] = (alpha_s * s_img[:, :, 0] + alpha_l * frame[y1:y2, x1:x2, 0])
                frame[y1:y2, x1:x2, 1] = (alpha_s * s_img[:, :, 1] + alpha_l * frame[y1:y2, x1:x2, 1])
                frame[y1:y2, x1:x2, 2] = (alpha_s * s_img[:, :, 2] + alpha_l * frame[y1:y2, x1:x2, 2])
                print("Pass right is Secure")

        return frame
