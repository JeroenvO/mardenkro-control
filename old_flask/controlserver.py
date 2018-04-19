import time
import json
import subprocess
from subprocess import TimeoutExpired
import threading


class lineThread(threading.Thread):
    def __init__(self, sio):
        self.sio = sio
        self.sio.emit('update', 'Init thread', namespace='/control')
        self.buffer = []
        # self.lineproc = subprocess.Popen(['python', './spammer.py'], stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        self.lineproc = subprocess.Popen(['./soccerline'], stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            p =self.lineproc.poll()
            if p is not None:
                error = ['read_line', 'no line proc. Code: '+str(p)]
                raise Exception(error)
            try:
                val = self.lineproc.stdout.readline()
                self.sio.emit('update', val, namespace='/line')
                try:
                    self.buffer.append(json.loads(val))
                except:
                    continue
                with open('tmp_line', 'w') as f:
                    f.write(val)
                    f.flush()
            except TimeoutExpired:
                self.lineproc.kill()
                outs, errs = self.lineproc.communicate()
                self.running = False
                error = ['read_line', 'timeout: '+str(errs)]
                raise Exception(error)
        self.lineproc.terminate()

    def get(self):
        if len(self.buffer)>0:
            return self.buffer.pop()
        return None

    def stop(self):
        self.running = False


class ControlThread(threading.Thread):
    def __init__(self, socketio):
        self.sio = socketio
        self.buffer = None
        self.error = False
        self.running = True
        self.control = False
        self.spray = False
        self.speed = 1

        self.linethread = lineThread(self.sio)
        self.linethread.start()
        super().__init__()


    def read_line(self):
        """
        Read input from the processed camera images

        :return:
        """
        return self.linethread.get()

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
        with open('tmp_log','w') as f:
            f.write('start loop')
            f.flush()
            self.sio.emit('update', 'run', namespace='/control')
            while self.running:
                # input
                try:
                    # self.sio.emit('update', 'poll line', namespace='/control')
                    val = self.read_line()
                    if val is not None:
                        a,b,c = val
                        self.sio.emit('update', json.dumps([val]), namespace='/control')
                    else:
                        # self.sio.emit('update', 'no line seen', namespace='/control')
                        continue
                except Exception as e:
                    self.sio.emit('update', 'E read_line '+str(e), namespace='/control')
                    print('Line read error: ' + str(e))
                    self.running=False
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
                    self.running=False
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
                    self.running=False
                    break
                self.sio.emit('update', 'loop', namespace='/control')
                f.write('loop')
                f.flush()
                time.sleep(0.5)
        # loop terminated.
        self.linethread.stop()
        self.linethread.join()
        self.sio.emit('update', 'Stop running', namespace='/control')
