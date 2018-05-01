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
s_speed = 10  # [0-250] speed setpoint
s_pump = 0   # [0-100] pump pwm control
s_valve = 0  # 0=water, 1=paint

def motor_control(client):
    """
    some control algorithm to convert offset, angle and linact_pos to a motor control command.

    :param offset: offset as seen by the camera. -1 to 1, 0 is center of image.
    :param angle: angle of the paint line as seen by the camera.
    :return: left and right motor position.
    """
    def disable():
        o_right = 0
        o_left = 0
        o_arm = a_arm
        pump = 0
        valve = 0
        client.sendMessage('UAuto disable'.encode('utf-8'))
        client.sendMessage(('C' + json.dumps([o_right, o_left, o_arm, pump, valve])).encode('utf-8'))

    global linact_post
    global buffer_arduino
    global buffer_line
    global running
    global s_speed
    global s_pump
    global s_valve
    client.sendMessage(u'Ustart controlloop thread'.encode('utf-8'))
    # left, right, arm, pump, valve
    max_diff = timedelta(seconds=2)
    while True:
        # control loop
        while running:
            now = datetime.now()
            # read arduino
            try:
                a_right, a_left, a_arm = buffer_arduino[1]  #
                a_right *= 100  # arduino sends motor speed in [0-2.5], raspi send motor speed in [0-250]
                a_left *= 100
                if buffer_arduino[0] - now > max_diff:
                    running = False
                    client.sendMessage('UArduino data too old, stopping control loop'.encode('utf-8'))
                    running = False
                    disable()
            except:
                client.sendMessage(('UArduino data failed {}, stopping control loop'.format(buffer_arduino)).encode('utf-8'))
                running = False
                disable()
            # read lines

            try:
                _, l_offset, l_angle, l_nlines = buffer_line[1]  # type, offset, angle (rad), #lines
                l_offset = -l_offset
                if buffer_line[0] - now > max_diff:
                    running = False
                    client.sendMessage('ULine follow data too old, stopping control loop'.encode('utf-8'))
            except:
                client.sendMessage(('ULine follow data failed {}, stopping control loop'.format(buffer_line)).encode('utf-8'))
                running = False
                disable()

            if running:
                # normal control
                i_arm = ci_arm(a_arm)  # current arm in meters
                real_offset = ci_offset(l_offset, l_angle)  # nozzle to line distance in meters
                print('ro{}'.format(real_offset))
                arm = control_arm(i_arm, real_offset)  # new arm position in meters
                o_arm = co_arm(arm)  # new arm position in ticks
                # if 50 < o_arm or o_arm > 900:
                #     arm_good = False
                #     client.sendMessage(('UControl error, Going to end of position {}'.format(o_arm)).encode('utf-8'))
                # else:
                #     arm_good = True
                d_speed = control_direction(l_angle, a_arm)  # difference in speed left/right. o_arm in ticks.
                speed = control_speed(s_speed, l_angle)
                o_left = round(speed - d_speed / 2)
                o_right = round(speed + d_speed / 2)
                client.sendMessage(('ULine follow data d{} s{} l{} r{}'.format(d_speed, speed, o_left, o_right)).encode('utf-8'))
                check = accuracy_good(l_nlines, l_angle, arm, a_right, o_right, a_left, o_left)
                if check[0]:
                    pump = s_pump
                    valve = s_valve
                else:
                    # override
                    pump = 0
                    valve = 0
                    o_right = 0
                    o_left = 0
                    o_arm = 500
                    client.sendMessage(('U' + 'Control error, overide, control disabled. ' + check[1]).encode('utf-8'))
                    running = False
                client.sendMessage(('C' + json.dumps([round(o_right), round(o_left), round(o_arm), round(pump), round(valve)])).encode('utf-8'))

            sleep(0.1)  # control loop run speed
        sleep(0.5)  # control loop check enabled speed


class ControlClient(WebSocketClientProtocol):
    def onOpen(self):
        self.sendMessage(u"UControl server connected".encode('utf8'))
        self.thread = Thread(target=motor_control, args=(self,))
        self.thread.start()

    def onMessage(self, payload, isBinary):
        global buffer_arduino
        global buffer_line
        global running
        global s_speed
        global s_pump
        global s_valve

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
                    try:
                        s_speed, s_pump, s_valve = json.loads(payload[2:])
                    except:
                        running = False
                elif payload[0] == 'A':
                    # print("rx: " + payload)
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
