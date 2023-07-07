#  CODE For Front vehicle model and  (Server socket)
'''
This Code is for Server socket and Front vehicle Computer vision model ,
that explain how to use socket as Server and how to send a video to the client
'''

# ------------------ Server Socket ---------------

import socket
import struct
import sys

import cv2

TCP_IP = '127.0.0.1'  # IP address of the server
TCP_PORT = 20080  # Port number

# Set up TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))

# Set up video capture
# cap = cv2.VideoCapture(0)  # 0 represents the default camera
video = cv2.VideoCapture("..\\gui\\front_cut.mp4")  # Read video
width, height = 500, 350  # Resize the Frame
# Exit if video not opened.
if not video.isOpened():
    print("Could not open video")
    sys.exit()

while True:
    ret, frame = video.read()  # read Frame by frame
    frame = cv2.resize(frame, (width, height))  # Resize the Frame
    # Exit if video not opened.
    if not ret:
        print('Cannot read video file')
        sys.exit()
        break
    #     # Read a frame from the camera
    #     ret, frame = cap.read()

    # Encode the frame as JPEG
    _, encoded_frame = cv2.imencode('.jpg', frame)

    # Get the size of the frame
    frame_size = len(encoded_frame)

    # Pack the frame size and frame data into a struct
    frame_info = struct.pack('!I', frame_size) + encoded_frame.tobytes()

    # Send the frame over TCP
    sock.sendall(frame_info)

    # Display the frame (optional)
    cv2.imshow('Video', frame)

    # Check for 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the resources
cap.release()
cv2.destroyAllWindows()
sock.close()

# ------------------ Front CV  ------------------

import cv2
import sys
from torch.hub import load


class MultiCarsdetection:
    def __init__(self, width, height, conf_threshold=0.2, area_threshold=13000):

        print("Loading Object Detection")
        print("Running YOLOv5n")
        self.model = load('ultralytics/yolov5', 'custom', path='best.pt')  # Load custom YOLOv5 model
        self.conf_threshold = conf_threshold  # Reject any predictions with confidence less than threshold
        self.area_threshold = area_threshold
        self.end_left_section = round(width / 3)
        self.end_middle_section = round(width / (3 / 2))
        self.end_right_section = width
        self.result = None
        self.width = width
        self.height = height

    def calc_area(self, xmin, ymin, xmax, ymax):
        '''
        calculate detected car area after rounded it 
        '''
        width = round(abs(xmax - xmin))
        height = round(abs(ymax - ymin))
        return width * height

    def get_car_center(self, x1, y1, x2, y2, width, height):
        c_x = round((abs(abs(width - x1) - abs(width - x2)) / 2) + x1)
        c_y = round((abs(abs(height - y1) - abs(height - y2)) / 2) + y1)
        center = (c_x, c_y)
        return center

    def detect(self, frame):
        self.result = self.model(frame)
        self.df = self.result.pandas().xyxy[0]

        # First: set the therashould for whole dataframe
        self.df = self.df[self.df['confidence'] > self.conf_threshold]

        if (not self.df.empty):  # check if the dataframe is empty after applying therashould

            # add Area Coulmn to data frame to get the highest car area
            self.df['area'] = self.df.apply(lambda x: self.calc_area(x['xmin'], x['ymin'], x['xmax'], x['ymax']),
                                            axis=1)

            print('======================================================================================')
            print('===================================== Cars Detection =================================')
            print('======================================================================================')
            print(self.df)
            #             print('--------------------------------------------------------------------------------------')
            highest_left_car_area = self.df[self.df['xmax'] <= self.end_left_section]
            if (not highest_left_car_area.empty):
                highest_left_car_area = self.df.iloc[highest_left_car_area['area'].idxmax()]
                #                 print('highest_left_car_area')
                #                 print("{}".format( highest_left_car_area))
                highest_left_car_area_center = self.get_car_center(x1=highest_left_car_area['xmin'],
                                                                   y1=highest_left_car_area['ymin'],
                                                                   x2=highest_left_car_area['xmax'],
                                                                   y2=highest_left_car_area['ymax'], width=self.width,
                                                                   height=self.height)
                x1y1 = (round(highest_left_car_area['xmin']), round(highest_left_car_area['ymin']))
                x2y2 = (round(highest_left_car_area['xmax']), round(highest_left_car_area['ymax']))
                cv2.rectangle(frame, x1y1, x2y2, (0, 0, 255), 2)
                cv2.circle(frame, highest_left_car_area_center, radius=1, color=(0, 0, 255), thickness=2)

            else:
                highest_left_car_area = 0
                highest_left_car_area_center = 0
            #             print('--------------------------------------------------------------------------------------')
            highest_middle_car_area = self.df[
                (self.df['xmax'] > self.end_left_section) & (self.df['xmax'] <= self.end_middle_section)]
            if (not highest_middle_car_area.empty):
                highest_middle_car_area = self.df.iloc[highest_middle_car_area['area'].idxmax()]
                #                 print('highest_middle_car_area')
                #                 print("{}".format( highest_middle_car_area))
                highest_middle_car_area_center = self.get_car_center(x1=highest_middle_car_area['xmin'],
                                                                     y1=highest_middle_car_area['ymin'],
                                                                     x2=highest_middle_car_area['xmax'],
                                                                     y2=highest_middle_car_area['ymax'],
                                                                     width=self.width, height=self.height)
                x1y1 = (round(highest_middle_car_area['xmin']), round(highest_middle_car_area['ymin']))
                x2y2 = (round(highest_middle_car_area['xmax']), round(highest_middle_car_area['ymax']))
                cv2.rectangle(frame, x1y1, x2y2, (0, 255, 0), 2)
                cv2.circle(frame, highest_middle_car_area_center, radius=1, color=(0, 255, 0), thickness=2)

            else:
                highest_middle_car_area = 0
                highest_middle_car_area_center = 0
            #             print('--------------------------------------------------------------------------------------')
            highest_right_car_area = self.df[
                (self.df['xmax'] > self.end_middle_section) & (self.df['xmax'] <= self.end_right_section)]
            if (not highest_right_car_area.empty):
                highest_right_car_area = self.df.iloc[highest_right_car_area['area'].idxmax()]
                #                 print('highest_right_car_area')
                #                 print("{}".format( highest_right_car_area))
                highest_right_car_area_center = self.get_car_center(x1=highest_right_car_area['xmin'],
                                                                    y1=highest_right_car_area['ymin'],
                                                                    x2=highest_right_car_area['xmax'],
                                                                    y2=highest_right_car_area['ymax'], width=self.width,
                                                                    height=self.height)
                x1y1 = (round(highest_right_car_area['xmin']), round(highest_right_car_area['ymin']))
                x2y2 = (round(highest_right_car_area['xmax']), round(highest_right_car_area['ymax']))
                cv2.rectangle(frame, x1y1, x2y2, (255, 0, 0), 2)
                cv2.circle(frame, highest_right_car_area_center, radius=1, color=(255, 0, 0), thickness=2)
            else:
                highest_right_car_area = 0
                highest_right_car_area_center = 0

            cars_sections = [highest_left_car_area_center, highest_middle_car_area_center,
                             highest_middle_car_area_center]
            return cars_sections  # return list of highest car area for each section, 0 left, 1 middel, 2 right
        else:
            return [0, 0, 0]





def run():
    # Some Initial  Parameters
    width, height = 1000, 700  # Resize the Frame

    # Detection Instances
    od = MultiCarsdetection(width=width, height=height)

    video = cv2.VideoCapture("front-view.mp4")  # Read video

    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()

    while True:
        ok, frame = video.read()  # read Frame by frame
        frame = cv2.resize(frame, (width, height))  # Resize the Frame

        # Exit if video not opened.
        if not ok:
            print('Cannot read video file')
            sys.exit()
            break

        cars_sections = od.detect(frame=frame)
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        print('Detected Left Car center  : ')
        print(cars_sections[0])
        print('Detected midel Car center : ')
        print(cars_sections[1])
        print('Detected right Car center : ')
        print(cars_sections[2])
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

        # Divide Frame Into Sections
        # Left section
        cv2.line(frame, (round(width / 3), 0), (round(width / 3), height), (0, 0, 0), 1)
        cv2.putText(frame, "Left Section", (5, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2);
        # Middle section
        cv2.line(frame, (round(width / (3 / 2)), 0), (round(width / (3 / 2)), height), (0, 0, 0), 1)
        cv2.putText(frame, "Middle Section", (round(width / 3) + 5, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0),
                    2);
        # Right section
        cv2.putText(frame, "Right Section", (round(width / (3 / 2)) + 5, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (255, 0, 0), 2);
        # Showing The Video Frame
        cv2.imshow('test_Image', frame)

        #         cv2.waitKey(0)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # if press q
            break

    video.release()
    cv2.destroyAllWindows()





run()


