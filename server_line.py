import subprocess

from autobahn.asyncio.websocket import WebSocketClientProtocol


#
# def read_line(lineproc):
#     p = lineproc.poll()
#     print("proc: "+str(p))
#     if p is not None:
#         error = ['read_line', 'no line proc. Code: ' + str(p)]
#         raise Exception(error)
#     try:
#         val = lineproc.stdout.readline()
#         print("val: "+str(val))
#         return val
#     except TimeoutExpired:
#         lineproc.kill()
#         outs, errs = lineproc.communicate()
#         running = False
#         error = ['read_line', 'timeout: ' + str(errs)]
#         raise Exception(error)

def read_lines(client):
    lineproc = subprocess.Popen(['./soccerline'], stdout=subprocess.PIPE, universal_newlines=False, bufsize=0, shell=False)
    client.sendMessage(str(lineproc).encode('utf-8'))

    while True:
        output = lineproc.stdout.readline()
        if output == '' and lineproc.poll() is not None:
            break
        if output:
            output = output.strip().decode('utf-8')
            print(output.strip())
            client.sendMessage(str('L'+str(output.strip())).encode('utf-8'))
    rc = lineproc.poll()
    return rc


class LineClient(WebSocketClientProtocol):

    def onOpen(self):
        self.sendMessage(u"Line reader connected".encode('utf8'))

        read_lines(self)
            # x = read_line(self.lineproc)
            # self.sendMessage(x.encode('utf-8'))
            # self.factory.loop.call_later(1, send_line)

    def onMessage(self, payload, isBinary):
        return

    def onClose(self, wasClean, code, reason):
        print("Line reader connection closed: {0}".format(reason))
        self.lineproc.terminate()


if __name__ == '__main__':
    import asyncio
    from autobahn.asyncio.websocket import WebSocketClientFactory

    factory = WebSocketClientFactory()
    factory.protocol = LineClient
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
