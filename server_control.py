import json
import subprocess
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from autobahn.asyncio.websocket import WebSocketClientProtocol
from control_conversion import *
from control_functions import *

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
            l_nlines, l_offset, l_angle, _ = buffer_line[1]  # type, offset, angle (rad), #lines
            if buffer_arduino[0] - now > max_diff:
                running = False
                client.sendMessage('UArduino data too old, stopping control loop')
                o_right = 0
                o_left = 0
                o_arm = a_arm
                pump = 0
                valve = 0
            elif buffer_line[0] - now > max_diff:
                running = False
                client.sendMessage('ULine follow data too old, stopping control loop')
                o_right = 0
                o_left = 0
                o_arm = a_arm
                pump = 0
                valve = 0
            else:
                # normal control
                i_arm = ci_arm(a_arm)                            # current arm in meters
                real_offset = ci_offset(l_offset, l_angle)       # nozzle to line distance in meters
                arm = control_arm(i_arm, real_offset)            # new arm position in meters
                o_arm = co_arm(arm)                              # new arm position in ticks
                d_speed = control_direction(l_angle, arm)        # difference in speed left/right
                setpoint_speed = 10
                speed = setpoint_speed * 1/(1+l_angle*mu_1)
                o_left = speed * (1-d_speed/2)
                o_right = speed * (1+d_speed/2)
                if accuracy_good(nlines, l_angle, arm, i_speed_left, i_speed_right):
                    pump = 100
                    valve = 1
                else:
                    # override
                    pump = 0
                    valve = 0
                    o_right = 0
                    o_left = 0
                    o_arm = 500
                    client.sendMessage('U' + 'Control error, overide, control disabled.')
                    running = False

            client.sendMessage('C' + json.dumps([o_right, o_left, o_arm, pump, valve])
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
            try:
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
                elif payload[0] == 'R':
                    print('restarting?')
                    if payload[1] == '1':
                        print('restarting!')
                        self.sendMessage(u"URebooting raspberry".encode('utf8'))
                        subprocess.run(['sudo', 'reboot'])
            except Exception as e:
                print(e)

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
