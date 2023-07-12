from communication.com_serial import *

sc = SerialComm(port="COM11", name="Sender", baudrate=115200)
print(sc)
simulated_distances = [7, 6, 5, 4, 3, 3, 2, 1, 2, 3, 3, 4, 5, 6, 7]
counter = 0
while True:
    if not sc.connection_state:
        data_to_send = {"DISTANCE": [simulated_distances[i] * counter * 10 for i in range(0, 15)]}
        print(data_to_send)
        counter = counter + 1
        counter = counter % 10
        sc.send_query(data_query=data_to_send)

    else:
        sc = SerialComm(port="COM11", name="Sender", baudrate=115200)
    time.sleep(1)
