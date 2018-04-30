import asyncio

from autobahn.asyncio.websocket import WebSocketClientFactory

global ser
from multiprocessing import Process
from time import sleep

import server_arduino
import server_control
import server_line
import server_message
from autobahn.asyncio.websocket import WebSocketClientProtocol

m = None
a = None
l = None
c = None

def startall():
    global m
    global a
    global l
    global c
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

    sleep(1)


def stopall():
    global m
    global a
    global l
    global c
    m.terminate()
    a.terminate()
    l.terminate()
    c.terminate()
    sleep(3)
    m.join()
    a.join()
    l.join()
    c.join()


startall()
