import serial
from autobahn.asyncio.websocket import WebSocketClientProtocol


class ArduinoClient(WebSocketClientProtocol):
    global ser
    def onOpen(self):
        self.sendMessage(u"Arduino server connected".encode('utf8'))
        def read_arduino():
            d = ser.readline()
            print("rx: "+str(d))
            self.sendMessage(d.encode('utf-8'))
            self.factory.loop.call_later(1, read_arduino)  # do this every second
        read_arduino()

    def onMessage(self, payload, isBinary):
        payload = payload.decode('utf-8')
        print("tx: "+payload)
        ser.write(payload)

    def onClose(self, wasClean, code, reason):
        print("Arduino server connection closed: {0}".format(reason))
        ser.close()

if __name__ == '__main__':
    import asyncio
    from autobahn.asyncio.websocket import WebSocketClientFactory

    ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)  # Open named port
    ser.baudrate = 9600  # Set baud rate to 9600

    factory = WebSocketClientFactory()
    factory.protocol = ArduinoClient
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
