import json
from threading import Thread

import serial
from autobahn.asyncio.websocket import WebSocketClientProtocol

BAUD = 115200
PORT = "/dev/serial0"


def read_arduino(client, ser):
    client.sendMessage(u'UArduino read thread started.'.encode('utf-8'))
    while True: #ser.in_waiting:
        try:
            d = str(ser.readline().decode())
            if d:
                try:
                    d = json.loads(d)
                    d = 'A'+d
                except:
                    d = 'U'+d
                # print(d)
                client.sendMessage(d.encode('utf-8'))
        except Exception as e:
            print("arduino read error {} !".format(e))

class ArduinoClient(WebSocketClientProtocol):
    global ser

    def onOpen(self):
        self.sendMessage(u"UArduino server connected.".encode('utf-8'))
        self.thread = Thread(target=read_arduino, args=(self, ser))
        self.thread.start()

    def onMessage(self, payload, isBinary):
        payload = payload.decode('utf-8')
        if payload[0] == 'C':  # only listen to control messages
            payload = payload[1:]+'\n'
            print("arduino tx: "+payload)
            ser.write(payload.encode())

    def onClose(self, wasClean, code, reason):
        print("UArduino server connection closed: {0}".format(reason))
        self.sendMessage(u"UArduino server disconnected".encode('utf-8'))
        ser.close()
        self.thread.join()

if __name__ == '__main__':
    import asyncio
    from autobahn.asyncio.websocket import WebSocketClientFactory

    ser = serial.Serial(PORT, BAUD, timeout=0.5)  # Open named port

    factory = WebSocketClientFactory()
    factory.protocol = ArduinoClient
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
