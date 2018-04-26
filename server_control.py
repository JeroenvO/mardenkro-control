import json
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from autobahn.asyncio.websocket import WebSocketClientProtocol

# globals
linact_post = 0  # position of horizontal moving boom.
buffer_arduino = ''
buffer_line = []
running = False


def motor_control(client):
    """
    some control algorithm to convert offset, angle and linact_pos to a motor control command.

    :param offset: offset as seen by the camera. -1 to 1, 0 is center of image.
    :param angle: angle of the paint line as seen by the camera.
    :return: left and right motor position.
    """
    def i_arm(arm):
        """
        Correct arm from steps to meters
        12.5cm per 500steps

        :param arm: input arm in steps [50-900]
        :return: arm distance in meters
        """
        arm_cm_per_step = 0.125/500
        return (arm-50) * arm_cm_per_step

    def o_arm(arm):
        """
        Calculate arm postition to steps
        12.5cm per 500steps

        :param arm: in meters
        :return: in steps [50-900]
        """
        arm_cm_per_step = 0.125/500
        return arm/arm_cm_per_step + 50

    def i_offset(offset, angle):
        """
        Calculate offset postition of camera to meters
        and correct for offset of sprayer to camera

        :param offset: in camera range [-1 to 1]
        :return: in meters
        """

        return offset


    def calculate_speed(a_arm, l_angle, l_offset):
        """

        :param a_arm:
        :param l_angle:
        :param l_offset:
        :return:
        """
        v_new = 1/(1+mu_1) * a_arm + l_offset

        return None

    global linact_post
    global buffer_arduino
    global buffer_line
    global running
    client.sendMessage(u'Ustart controlloop thread'.encode('utf-8'))
    # left, right, arm, pump, valve
    max_diff = timedelta(seconds=2)
    while True:
        # control loop
        while running:
            now = datetime.now()
            a_right, a_left, a_arm = buffer_arduino[1] #
            _, l_offset, l_angle, _ = buffer_line[1]  # type, offset, angle (rad), #lines
            if buffer_arduino[0] - now > max_diff:
                running = False
                client.sendMessage('UArduino data too old, stopping control loop')
                right = 0
                left = 0
                arm = a_arm
                pump = 0
                valve = 0
            elif buffer_line[0] - now > max_diff:
                running = False
                client.sendMessage('ULine follow data too old, stopping control loop')
                right = 0
                left = 0
                arm = a_arm
                pump = 0
                valve = 0
            else:
                # normal control
                right = 0
                left = 0
                arm = a_arm
                pump = 0
                valve = 0
            client.sendMessage('C' + json.dumps([right, left, arm, pump, valve])
                               .format(linact_post, buffer_arduino,
                                       buffer_line).encode('utf-8'))

            sleep(0.5)  # control loop run speed
        sleep(1)  # control loop check enabled speed


class ControlClient(WebSocketClientProtocol):
    def onOpen(self):
        self.sendMessage(u"UControl server connected".encode('utf8'))
        self.thread = Thread(target=motor_control, args=(self,))
        self.thread.start()

    def onMessage(self, payload, isBinary):
        global buffer_arduino
        global buffer_line
        global running
        payload = payload.decode('utf-8')
        if payload:
            if payload[0] == 'L':  # Line input messages
                # type, offset, angle, nlines
                try:
                    buffer_line = [datetime.now(), json.loads(payload[1:])]
                    assert len(buffer_line) == 4  # check length of payload
                except:
                    pass
            if payload[0] == 'F':  # line Follower enable
                running = payload[1]
                print("Set running to {}".format(running))
            elif payload[0] == 'A':
                print("rx: " + payload)
                buffer_arduino = [datetime.now(), json.loads(payload[1:])]

    def onClose(self, wasClean, code, reason):
        self.sendMessage("UControl loop connection closed: {0}".format(reason).encode('utf-8'))
        print("Control loop connection closed: {0}".format(reason))
        self.thread.join()


def run():
    import asyncio
    from autobahn.asyncio.websocket import WebSocketClientFactory

    factory = WebSocketClientFactory()
    factory.protocol = ControlClient
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    run()
