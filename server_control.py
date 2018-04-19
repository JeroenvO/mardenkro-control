import json
from autobahn.asyncio.websocket import WebSocketClientProtocol

linact_post = 0  # position of horizontal moving boom.

def motor_control(offset, angle):
    """
    some control algorithm to convert offset, angle and linact_pos to a motor control command.

    :param offset: offset as seen by the camera. -1 to 1, 0 is center of image.
    :param angle: angle of the paint line as seen by the camera.
    :return: left and right motor position.
    """
    global linact_post
    #TODO @bakelnaar
    left, right = 1, 1
    return [left, right]


class ControlClient(WebSocketClientProtocol):
    global ser
    def onOpen(self):
        self.sendMessage(u"Control server connected".encode('utf8'))

    def onMessage(self, payload, isBinary):
        payload = payload.decode('utf-8')
        if payload[0] == 'L':  # only listen to line messages
            print("rx: "+payload)
            type, offset, angle, nlines = json.loads(payload[1:])  # decode line input
            motoraction = motor_control(offset, angle)
            # send as control action to server_message, server_arduino will relay it.
            self.sendMessage('C'+json.dumps(motoraction))

    def onClose(self, wasClean, code, reason):
        print("Arduino server connection closed: {0}".format(reason))
        ser.close()

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
