from autobahn.asyncio.websocket import WebSocketServerProtocol

clients = []


# send data to all autobahn clients
def sendData(data):
    global clients
    for client in clients:
        if client:
            client.sendMessage(data, 0)
            print("sending!" + data)
        else:
            print("invalid client!")

class MessageServer(WebSocketServerProtocol):
    def onConnect(self, request):
        global clients
        clients.append(self)
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))

    def onMessage(self, payload, isBinary):
        # forward message to others.
        print("WS message received: " + payload.decode('utf-8'))
        global clients
        for client in clients:
            if client != self:
                client.sendMessage(payload, isBinary=False)


if __name__ == '__main__':
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
