import time
from threading import Thread

from communication.com_serial import SerialComm

sc = SerialComm(port="COM11", name="Receiver", baudrate=115200)
print(sc)


def fetcher():
    dist_list = []
    while True:
        temp_holder = sc.receive_query()
        print(type(temp_holder))
        if type(temp_holder) is dict:
            print(temp_holder["DISTANCE"][0])
            print(temp_holder["DISTANCE"][7])
            print(temp_holder["DISTANCE"][14])
            if temp_holder:
                dist_list = [section for section in sc.receive_query()]
            print(f"Test_App: {dist_list}, Length={len(dist_list)}")
            time.sleep(0.1)


t = Thread(target=fetcher, args=[], daemon=True)
t.start()
while True:
    time.sleep(1)

    print("main App")
