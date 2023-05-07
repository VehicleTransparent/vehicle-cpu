from communication.com_socket import Server
import cv2, pickle, struct, time


s = Server(ip="127.0.0.1", port=20070, timeout=3)

vid = cv2.VideoCapture(0)
while(vid.isOpened()):
    img,frame = vid.read()
    cv2.imshow('SOCK_Sending This Frame...', frame)
    s.send_all({"F":frame, "D":[0,2,4]})
    key = cv2.waitKey(10)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # if press q
        # sys.exit()
        break
cv2.destroyAllWindows()
