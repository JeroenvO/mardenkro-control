from multiprocessing import Process
from time import sleep

import server_arduino
import server_control
import server_line
import server_message


if __name__ == '__main__':
    sleep(1)

    print("Starting message server")
    m = Process(target=server_message.run)
    m.start()

    sleep(2)

    print("Starting arduino server")
    a = Process(target=server_arduino.run)
    a.start()

    print("Starting line server")
    l = Process(target=server_line.run)
    l.start()

    sleep(1)

    print("Starting control server")
    c = Process(target=server_control.run)
    c.start()
