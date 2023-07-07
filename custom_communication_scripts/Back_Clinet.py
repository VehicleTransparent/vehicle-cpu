#  CODE For Back vehicle model and  (Client socket)
'''
This Code is for client socket an Back vehicle Computer vision model ,
that explain how to use socket as client and how to use the received video to fill it
over the detected vehicle
'''

#  --------------- Client Socket ---------
import socket
import struct

import numpy as np

TCP_IP = '127.0.0.1'  # IP address of the server
TCP_PORT = 20080  # Port number
sock, conn, addr = None, None, None


def init_soc():
    global sock, conn, addr

    # Set up TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, TCP_PORT))
    sock.listen(1)
    # Accept a client connection
    conn, addr = sock.accept()


def receive():
    global conn
    # Receive the frame size
    frame_size_data = conn.recv(4)
    frame_size = struct.unpack('!I', frame_size_data)[0]

    # Receive the frame data
    frame_data = b""
    while len(frame_data) < frame_size:
        data = conn.recv(frame_size - len(frame_data))
        if not data:
            break
        frame_data += data

    # Convert the frame data to a NumPy array
    frame = np.frombuffer(frame_data, dtype=np.uint8)

    # Decode the frame as an image
    frame = cv2.imdecode(frame, 1)

    # Display the received frame if valid
    if frame is not None:
        cv2.imshow('Received Frame', frame)
        return frame
    else:
        return None
    # Check for 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return None


#  --------------- Back CV ---------------
import cv2
import sys
import torch
from torch.hub import load
import math


class SingleCarDetection:
    def __init__(self, conf_threshold=0.2, area_threshold=13000):
        print("Loading Object Detection")
        print("Running custom YOLOv5 model")
        self.model = load('ultralytics/yolov5', 'custom', path='best.pt')  # Load custom YOLOv5 model
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
        """
            Perform object detection on the given frame and return relevant information about the nearest car to 
        the ROI center after filtering all detected cars with a confidence and Area threshold.

        Args:
            frame (torch.Tensor): Input frame for object detection.
            roi_center (tuple): Tuple representing the center coordinates of the Region of Interest (ROI).

        Returns:
            int: x1 - x-coordinate of the top-left corner of the bounding box around the nearest detected car.
            int: y1 - y-coordinate of the top-left corner of the bounding box around the nearest detected car.
            int: x2 - x-coordinate of the bottom-right corner of the bounding box around the nearest detected car.
            int: y2 - y-coordinate of the bottom-right corner of the bounding box around the nearest detected car.
            str: text - Text label for the nearest detected car, including class label and confidence score.
            float: conf - Confidence score of the nearest detected car.
            int: area - Area of the bounding box around the nearest detected car.

        """
        result = self.model(frame)
        df = result.pandas().xyxy[0]
        df = df[df['confidence'] > self.conf_threshold]
        if not df.empty:
            df['area'], df['center'] = zip(
                *df.apply(lambda x: self.calc_area_and_center(x['xmin'], x['ymin'], x['xmax'], x['ymax']), axis=1))

            df = df[df['area'] > self.area_threshold]  # Filter out areas less than 13000
            if not df.empty:
                df['distance_to_roi'] = df['center'].apply(
                    lambda x: self.distance(roi_center, x))  # Calculate distance from roi_center to car centers
                nearest_car = df[df['distance_to_roi'] == df['distance_to_roi'].min()].iloc[0]  # Get nearest car
                x1, y1 = int(nearest_car['xmin']), int(nearest_car['ymin'])
                x2, y2 = int(nearest_car['xmax']), int(nearest_car['ymax'])
                label = nearest_car['name']
                conf = nearest_car['confidence']
                text = f"{label}, {conf:.2f}"
                area = nearest_car['area']
                return x1, y1, x2, y2, text, conf, area
        return 0, 0, 0, 0, '', 0.0, 0


def video_filling_coordinates(x1, y1, x2, y2, detected_car_width, detected_car_height):
    new_detected_car_width = round(detected_car_width * 0.9)
    new_detected_car_height = round(detected_car_height * 0.33)
    x1 = round(x1 + detected_car_width * 0.05)
    y1 = round(y1 + detected_car_height * 0.3)
    x2 = round(x2 - detected_car_width * 0.05)
    y2 = round(y2 - detected_car_height * 0.3)
    return x1, y1, x2, y2, new_detected_car_width, new_detected_car_height


def run():
    # Some Initial Parameters
    width, height = 1366, 768  # ReSize the Frame
    x1, y1, x2, y2, text, conf, area, bbox, fps = 0, 0, 0, 0, '', 0, 0, 0, 0  # Initialize The x1, y1, x2, y2, text, conf, bbox
    C_X, C_Y, = int(width / 2), int(
        height / 2)  # Selecting the center for ROI 'region of interest', and its left and right distance.
    area_threshold = (
                             width * height) / 55  # Setting the threshold area by multiplying the width by height and dividing them by 55, 'we get this number by trying and catch with several use cases'.
    # Detection And Tracking Instances
    od = SingleCarDetection(area_threshold=area_threshold)
    init_soc()
    video = cv2.VideoCapture("..\\gui\\rear_cut.mp4")  # Read video
    logo = cv2.imread('Valeo.png')
    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()
    while True:
        ok, frame = video.read()  # read Frame by frame
        S_frame = receive()  # Read Streamed video

        # Exit if video not opened.
        if not ok:
            print('Cannot read video file')
            sys.exit()

        # Replace The StreamedData with Streamed Frame if it's not None else make it take logo Image
        if S_frame is None:
            print('Cannot read Streamed video file')
            S_frame = logo
        else:
            S_frame = S_frame

        if ok:
            timer = cv2.getTickCount()  # Start timer To Calculate FPS
            frame = cv2.resize(frame, (width, height))  # Resize the Frame
            roi_center = (C_X, (C_Y + (C_Y // 2)))
            x1, y1, x2, y2, text, conf, area = od.detect(frame=frame, roi_center=(C_X, C_Y))  # detecting a car in ROI
            detected_car_width = round(abs(x2 - x1))
            detected_car_height = round(abs(y2 - y1))

            x1, y1, x2, y2, detected_car_width, detected_car_height = video_filling_coordinates(x1, y1, x2, y2,
                                                                                                detected_car_width,
                                                                                                detected_car_height)
            detected_car_width = round(abs(x2 - x1))
            detected_car_height = round(abs(y2 - y1))
            # Fill Streamed Video
            if area != 0:
                S_frame = cv2.resize(S_frame, (detected_car_width, detected_car_height))
                frame[y1: y2, x1: x2] = cv2.addWeighted(frame[y1: y2, x1: x2], 0.2, S_frame, 0.9, 0)

                # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255,255), 1)
            x1, y1, x2, y2, text, area = 0, 0, 0, 0, '', 0
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);  # Calculate Frames per second (FPS)
            # Display FPS on frame
            cv2.putText(frame, "FPS : " + str(int(fps)), (23, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 255, 255), 2);
            cv2.imshow('Frame', frame)
        else:
            sys.exit()
        if cv2.waitKey(1) & 0xFF == ord('q'):  # if press SPACE
            break
    #         cv2.waitKey(0)

    video.release()
    cv2.destroyAllWindows()
    conn.close()
    sock.close()


run()
