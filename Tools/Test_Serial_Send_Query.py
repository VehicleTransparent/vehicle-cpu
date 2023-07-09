from communication.com_serial import *

sc = SerialComm(port="COM11", name="Sender", baudrate=115200)
print(sc)
a, b, c = 0, 0, 0
while True:
    # a, b, c = a + 1, b + 1, c + 1
    a = {"DISTANCE": [i * 10 for i in range(0, 15)]}
    print(a)

    sc.send_query(data_query=a)
    time.sleep(0.4)
