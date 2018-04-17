import json
import subprocess
from subprocess import TimeoutExpired
import threading

class ControlThread(threading.Thread):
    def __init__(self, socketio):
        self.sio = socketio
        self.buffer = None
        self.error = False
        self.running = True
        self.control = False
        self.spray = False
        self.speed = 1
        self.sio.emit('update','Init thread', namespace='/control')
        self.lineproc = subprocess.Popen(['python', './spammer.py'], shell=True, stdin=None, stdout=subprocess.PIPE, universal_newlines=True)

        super().__init__()

    def read_line(self):
        """
        Read input from the processed camera images

        :return:
        """
        if self.lineproc.poll() is not None:
            error = ['read_line', 'no line proc. Code: '+str(self.lineproc.poll())]
            raise Exception(error)
        try:
            val = self.lineproc.stdout.readline()
            self.sio.emit('update', val, namespace='/line')
            return json.loads(val)
        except TimeoutExpired:
            self.lineproc.kill()
            outs, errs = self.lineproc.communicate()
            running = False
            error = ['read_line', 'timeout: '+str(errs)]
            raise Exception(error)

    def motor_control(offset, angle, boom):
        """
        Calculate left and right motor speeds based on inputs

        :param offset: offset of the line.
        :param angle: angle of the line
        :param boom: How far the boom is out
        :return:
        """
        return (1,1)

    def motor_manual(self):
        """
        Calculate motor positions based on input buffer

        :return:
        """
        b=self.buffer
        s=self.speed
        if b=='n':
            return (s,s)
        if b=='s':
            return (-s,-s)
        if b=='w':
            return (0,s)
        if b=='e':
            return (s,0)

    def send_arduino(self, command):
        print("arduiono: "+command)

    def recv_arduino(self):
        return None

    def stop(self):
        """
        Function to stop the thread

        :return:
        """
        self.running = False

    def run(self):
        self.sio.emit('update', 'run', namespace='/control')
        while self.running:
            # input
            try:
                self.sio.emit('update', 'poll line', namespace='/control')
                offset, angle = self.read_line()
                self.sio.emit('update', json.dumps([offset, angle]), namespace='/control')
            except Exception as e:
                self.sio.emit('update', 'E read_line '+str(e), namespace='/control')
                print('Line read error: ' + str(e))
                break

            # calculation
            if self.control:
                left, right = self.motor_control(offset, angle)
            elif self.buffer:
                left, right = self.motor_manual()
                self.buffer = None
            else:
                # nothing to do.
                continue

            # output
            try:
                self.send_arduino('M[{0:.2f},{0:.2f}]'.format(left,right))
            except Exception as e:
                self.sio.emit('update', 'E send_arduino1 '+str(e), namespace='/control')
                print('Arduino send error: '+str(e))
                break
            if self.spray is not None:
                if self.spray == True:
                    c = 'S1'
                elif self.spray == False:
                    c = 'S0'
                try:
                    self.send_arduino(c)
                    self.spray=None
                except Exception as e:
                    self.sio.emit('update', 'E send_arduino2 '+str(e), namespace='/control')
                    print('Arduino send error: '+str(e))
                    break

            try:
                val = self.recv_arduino()
                self.sio.emit('update', val, namespace='/control')
            except Exception as e:
                self.sio.emit('update', 'E recv_arduino '+str(e), namespace='/control')
                print('Arduino recv error: '+str(e))
                break
            self.sio.emit('update', 'loop', namespace='/control')

        # loop terminated.

        self.lineproc.terminate()
        self.lineproc.kill()
        self.sio.emit('update', 'Stop running', namespace='/control')
