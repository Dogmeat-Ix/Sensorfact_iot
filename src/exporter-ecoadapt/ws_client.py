import logging

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

log = logging.getLogger(__name__)

SUBPROTOCOL = "sensorfact"


class SensorClientProtocol(WebSocketClientProtocol):
    """Sends sensor readings as JSON over WebSocket."""

    def onOpen(self):
        log.info("WebSocket connection open")
        self.factory.ws_protocol = self

    def onClose(self, wasClean, code, reason):
        log.info("WebSocket closed: %s" % reason)


def create_ws_factory(url):
    """Create a WebSocket client factory configured with our subprotocol."""
    factory = WebSocketClientFactory(url, protocols=[SUBPROTOCOL])
    factory.protocol = SensorClientProtocol
    factory.setProtocolOptions(openHandshakeTimeout=0)
    factory.ws_protocol = None
    return factory
