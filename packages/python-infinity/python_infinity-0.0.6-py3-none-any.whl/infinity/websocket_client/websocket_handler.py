import threading


class WebsocketHandler:
    """
    Websocket handler to record individual websocket connection

    ws_id(str): websocket unique ID
    client(Websocket.WebsocketApp): websocket app
    request_id: request ID for websocket
    reconnect_count(int) = websocket reconnection count

    """
    def __init__(self):
        self.ws_id = None
        self.client = None
        self.request_id = 1
        self.reconnect_count = 0
        self.subscribed_channels = []
        self.reconnect_lock = threading.Lock()
        self.is_open = False
        self.force_reconnect_event = None
        self.last_reconnect_timestamp = None