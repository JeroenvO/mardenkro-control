from autobahn.asyncio.websocket import WebSocketServerProtocol

clients = []


class MessageServer(WebSocketServerProtocol):
    def onConnect(self, request):
        global clients
        clients.append(self)
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))
        global clients
        for client in clients:
            if client != self:
                client.sendMessage('UError, some connection dropped!'.encode('utf-8'), isBinary=False)

    def onMessage(self, payload, isBinary):
        # forward message to others.
        # print("WS message received: " + payload.decode('utf-8'))
        global clients
        for client in clients:
            if client != self:
                client.sendMessage(payload, isBinary=False)

def run():
    import asyncio
    from autobahn.asyncio.websocket import WebSocketServerFactory

    factory = WebSocketServerFactory()
    factory.protocol = MessageServer

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

if __name__ == '__main__':
    run()
