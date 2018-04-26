import subprocess
import time
from autobahn.asyncio.websocket import WebSocketClientProtocol

def read_lines(client):
    lineproc = subprocess.Popen(['./soccerline'], stdout=subprocess.PIPE, universal_newlines=False, bufsize=0, shell=False)
    client.sendMessage(str(lineproc).encode('utf-8'))
    i = 0
    start = time.time()

    while True:
        output = lineproc.stdout.readline()
        if output == '' and lineproc.poll() is not None:
            break
        if output:
            output = output.strip().decode('utf-8')
            # print(output.strip())
            client.sendMessage(str('L'+str(output.strip())).encode('utf-8'))
        i += 1
        if i == 10:
            # elapsed time for 10 measurements
            diff = time.time() - start
            client.sendMessage(str('T{:.2f}'.format(10/diff)).encode('utf-8'))
            i = 0
            start = time.time()
    rc = lineproc.poll()
    return rc


class LineClient(WebSocketClientProtocol):
    def onOpen(self):
        self.sendMessage(u"ULine reader connected".encode('utf8'))
        read_lines(self)

    def onMessage(self, payload, isBinary):
        return

    def onClose(self, wasClean, code, reason):
        print("ULine reader connection closed: {0}".format(reason))
        self.sendMessage(u"ULine reader connection closed.".encode('utf8'))
        self.lineproc.terminate()


def run():
    import asyncio
    from autobahn.asyncio.websocket import WebSocketClientFactory

    factory = WebSocketClientFactory()
    factory.protocol = LineClient
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    run()