import json
from datetime import datetime
from threading import Thread
from time import sleep

from autobahn.asyncio.websocket import WebSocketClientProtocol

#globals
linact_post = 0  # position of horizontal moving boom.
buffer_arduino = ''
buffer_line = []


def motor_control(client):
    """
    some control algorithm to convert offset, angle and linact_pos to a motor control command.

    :param offset: offset as seen by the camera. -1 to 1, 0 is center of image.
    :param angle: angle of the paint line as seen by the camera.
    :return: left and right motor position.
    """
    global linact_post
    global buffer_arduino
    global buffer_line
    client.sendMessage(u'Ustart controlloop thread'.encode('utf-8'))
    while True:
        client.sendMessage("control loop. \n"
                           "lina: {}\n"
                           "ardu: {}\n"
                           "line: {}".format(linact_post, buffer_arduino, buffer_line).encode('utf-8'))
        sleep(1)


class ControlClient(WebSocketClientProtocol):
    def onOpen(self):
        self.sendMessage(u"UControl server connected".encode('utf8'))
        self.thread = Thread(target=motor_control, args=(self,))
        self.thread.start()

    def onMessage(self, payload, isBinary):
        global buffer_arduino
        global buffer_line
        payload = payload.decode('utf-8')
        if payload[0] == 'L':  # only listen to line messages
            # type, offset, angle, nlines
            try:
                buffer_line = [datetime.now(), json.loads(payload[1:])]
                assert len(buffer_line) == 4  # check length of payload
            except:
                pass
        elif payload[0] == 'A':
            print("rx: " + payload)
            buffer_arduino = [datetime.now(), payload[1:]]

    def onClose(self, wasClean, code, reason):
        print("UControl loop connection closed: {0}".format(reason))
        self.thread.join()


if __name__ == '__main__':
    import asyncio
    from autobahn.asyncio.websocket import WebSocketClientFactory

    factory = WebSocketClientFactory()
    factory.protocol = ControlClient
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
