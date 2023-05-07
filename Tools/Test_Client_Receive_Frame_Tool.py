import time, cv2

from communication.com_socket import Client
received_frames = Client(ip='127.0.0.1', port=20070, name="Frame Receive")

while True:
    received_frame, discrete = received_frames.receive_all(1024)
    window_name = 'Current Front'

    cv2.imshow(window_name, received_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # if press q
        # sys.exit()
        break
cv2.destroyAllWindows()

