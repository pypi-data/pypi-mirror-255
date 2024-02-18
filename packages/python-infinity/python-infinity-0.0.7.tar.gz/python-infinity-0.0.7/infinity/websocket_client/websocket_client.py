import json
import logging
import threading
import time
import traceback
from collections import deque
from datetime import datetime
from functools import partial

import websocket

from infinity.login.infinity_login import LoginClient
from infinity.utils import RepeatTimer, create_thread_with_kwargs, get_default_logger, generate_uuid, \
    get_current_utc_timestamp
from infinity.websocket_client import constants
from infinity.websocket_client.websocket_handler import WebsocketHandler


class WebSocketClient:
    def __init__(self, ws_url: str = None, login: LoginClient = None, reconnect_interval: int = 86400,
                 auto_reconnect_retries: int = 0, logger: logging.Logger = None):
        """
        Initializes the InfinityWebsocket object.

        Args:
            ws_url (str): Websocket
            login (LoginClient): login to use private websocket
            reconnect_interval (int): reconnect interval for websocket, default is 86400 seconds (24hours)
            auto_reconnect_retries (int): The number of times to attempt auto-reconnection in case of disconnection.
            logger (logging.Logger): The logger object to use for logging.
        """
        # websocket.enableTrace(True)
        self._ws_clients = {
            "public": WebsocketHandler(), "private": WebsocketHandler()
        }
        self._logger = logger
        self.__ping_timeout = 30
        self.__ping_interval = 60
        self._ws_url = ws_url
        self.__reconnect_interval = reconnect_interval
        self._inf_login = login
        self._auto_reconnection_retries = auto_reconnect_retries
        self._subscribed_data_dict = {
            constants.CHANNEL_USER_TRADE: deque([]),
            constants.CHANNEL_ORDER_BOOK: deque([]),
            constants.CHANNEL_USER_ORDER: deque([]),
            constants.CHANNEL_RECENT_TRADES: deque([])
        }

        if logger is None:
            self._logger = get_default_logger()

        if self._inf_login:
            if not self._inf_login.is_login_success():
                self._logger.error("Cannot login, please check login details")

    def run_all(self) -> None:
        """
        Runs the public and private WebSocket clients in separate threads and waits for the connections to be
        established.

        This method creates separate threads for the public and private WebSocket clients using the
        `create_public_client` and `create_private_client` methods. It starts both threads and waits until both
        connections are established before returning.

        Note: This method should be called after initializing the `InfinityWebsocket` object and performing the login
        process if required.

        Returns:
            None

        Example:
            websocket_client = InfinityWebsocketClient(ws_url="websocket url",
                                          login=infinity_login, reconnect_interval=86400,
                                          auto_reconnect_retries=3, logger=my_logger)
            websocket_client.run_all()
        """
        self._logger.info("Initializing Infinity Public Websocket...")
        start_t = get_current_utc_timestamp()
        public_thread = self.create_ws_thread(is_private=False)
        public_thread.start()
        if self._inf_login:
            self._logger.info("Initializing Infinity Private Websocket...")
            private_thread = self.create_ws_thread(is_private=True)
            private_thread.start()
            while not (self.is_private_connected() and self.is_public_connected()):
                time.sleep(0.001)  # Adjust the delay as needed
            public_ws_id = self._ws_clients["public"].ws_id
            private_ws_id = self._ws_clients["private"].ws_id
            log = ("Infinity Exchange public websocket(id=" + public_ws_id +
                   ") and private Websocket(id=" + private_ws_id + ") are connected")
        else:
            while not self.is_public_connected():
                time.sleep(0.001)  # Adjust the delay as needed
            public_ws_id = self._ws_clients["public"].ws_id
            log = f"Infinity Public Websocket(id={public_ws_id}) is connected"
        time_spent = get_current_utc_timestamp() - start_t
        self._logger.info(f"{log}, time spent = {time_spent} seconds.")

    def is_public_connected(self) -> bool:
        """
        Check if the public WebSocket connection is currently connected.

        Returns:
            bool: True if the connection is active, False otherwise.
        """
        key = "public"
        ws_client = self._ws_clients[key].client
        if ws_client is None:
            return False
        elif ws_client.sock is None:
            return False
        else:
            return ws_client.sock.connected and self._ws_clients[key].is_open

    def is_private_connected(self) -> bool:
        """
        Check if the private WebSocket connection is currently connected.

        Returns:
            bool: True if the connection is active, False otherwise.
        """
        key = "private"
        ws_client = self._ws_clients[key].client
        if ws_client is None:
            return False
        elif ws_client.sock is None:
            return False
        else:
            return ws_client.sock.connected and self._ws_clients[key].is_open

    def create_ws_thread(self, is_private: bool = False) -> threading.Thread:
        """
        Creates a thread that connects to the private Infinity server.
        User need to log in first to get access token before connecting private websocket.

        Args:
            is_private(bool): flag to determine private or public websocket use, default is False as public websocket.

        Returns:
            threading.Thread: A thread of the private WebSocket session.
        """
        if is_private and not self._inf_login.is_login_success():
            self._logger.info("Please login before running private infinity client.")
        else:
            key = "private" if is_private else "public"
            self.create_ws(is_private=is_private)
            return create_thread_with_kwargs(func=self._ws_clients[key].client.run_forever,
                                             kwargs={"ping_timeout": self.__ping_timeout,
                                                     "ping_interval": self.__ping_interval})

    def create_ws(self, is_private: bool = False) -> None:
        """
        The public_connect function is used to connect the public websocket client.

        Args:
            is_private(bool): flag to determine private or public websocket use, default is False as public websocket.

        Returns:
            None
        """
        key = "private" if is_private else "public"
        self._logger.debug(f"Connecting infinity {key} websocket client...")
        new_ws_id = generate_uuid()
        new_ws = websocket.WebSocketApp(self._ws_url)
        # if is_private:
        #     ws_header = "Authorization: Bearer " + self._inf_login.get_access_token()
        #     new_ws.header = [ws_header]
        new_ws.on_open = partial(self.on_open, ws_id=new_ws_id)
        new_ws.on_message = partial(self.on_message, ws_id=new_ws_id)
        new_ws.on_close = partial(self.on_close, ws_id=new_ws_id)
        new_ws.on_error = partial(self.on_error, ws_id=new_ws_id)
        new_ws.on_ping = partial(self.on_ping, ws_id=new_ws_id)
        new_ws.on_pong = partial(self.on_pong, ws_id=new_ws_id)

        old_ws = self._ws_clients[key].client
        if old_ws is not None:
            old_ws_id = self._ws_clients[key].ws_id
            self._logger.info(f"Expired {key} websocket connection (id={old_ws_id}) will be renewed.")
            self._ws_clients[key].client.close()
            # wait for websocket close
            if is_private:
                while self.is_private_connected():
                    time.sleep(0.001)  # Adjust the delay as needed
            else:
                while self.is_public_connected():
                    time.sleep(0.001)  # Adjust the delay as needed
        self._ws_clients[key].ws_id = new_ws_id
        self._ws_clients[key].client = new_ws

    def resubscribe_channels(self, is_private: bool = False) -> None:
        """
        Re-subscribe to previously subscribed channels after reconnecting private websocket connection.

        Args:
            is_private(bool): flag to determine private or public websocket use, default is False as public websocket.

        Returns:
            None
        """
        key = "private" if is_private else "public"
        subscribed_channels = self._ws_clients[key].subscribed_channels
        self._logger.info(f"Re-subscribe to {key} channels = {subscribed_channels}")
        resubscribe = {
            "method": "SUBSCRIBE",
            "params": subscribed_channels
        }
        self.send_message(message=resubscribe, is_private=is_private)

    def re_connect(self, is_private: bool = False) -> bool:
        """
        Reconnect websocket session. This function will close the old websocket session and re-establish a new session.

        Args:
            is_private(bool): flag to determine private or public websocket use, default is False as public websocket.

        Returns:
            bool: reconnected or not
        """
        key = "private" if is_private else "public"

        if self._ws_clients[key].reconnect_lock.locked():
            self._logger.debug(f"{key} websocket is reconnecting, ignore duplicate reconnection.")
            return False
        else:
            with self._ws_clients[key].reconnect_lock:
                thread = self.create_ws_thread(is_private=is_private)
                thread.start()
                if is_private:
                    while not self.is_private_connected():
                        time.sleep(0.001)  # Adjust the delay as needed
                else:
                    while not self.is_public_connected():
                        time.sleep(0.001)  # Adjust the delay as needed
                self.resubscribe_channels(is_private=is_private)
            self._ws_clients[key].last_reconnect_timestamp = get_current_utc_timestamp()
            return True

    def re_connect_on_unexpected(self, is_private: bool = False) -> None:
        """
        The re_connect_public function is used to re-connect the Infinity public websocket client.
        It will attempt to reconnect for a number of times specified by the user when user initialize
        InfinityWebsocket. (param: auto_reconnection_retries)
        If it fails, it will log a warning message and stop trying.

        Args:
            is_private(bool): flag to determine private or public websocket use, default is False as public websocket.

        Returns:
            None
        """
        key = "private" if is_private else "public"
        curr_reconnect_count = self._ws_clients[key].reconnect_count
        if self._auto_reconnection_retries == 0:
            self._logger.info("Auto-reconnection is disabled.")
        elif curr_reconnect_count >= self._auto_reconnection_retries:
            self._logger.warning("Cannot re-connect Infinity Exchange.")
        else:
            self._logger.info(
                f"Re-connecting Infinity {key} websocket. Previous reconnects: {curr_reconnect_count}")
            curr_t = get_current_utc_timestamp()
            if (curr_t - self._ws_clients[key].last_reconnect_timestamp) < self.__reconnect_interval:
                self._logger.warning(f"catch unexpected re-connection on {key} websocket, time = {curr_t}.")
            reconnected = self.re_connect(is_private=is_private)
            if reconnected:
                self._ws_clients[key].reconnect_count += 1

    def disconnect_all_ws_connection(self) -> None:
        """
        The disconnect function is used to close the websocket connection on
        both private and public websockets.

        Returns:
            None
        """
        self._logger.debug(f"Disconnecting websocket client..")
        for key in ["private", "public"]:
            self._ws_clients[key].force_reconnect_event.cancel()
            if self._ws_clients[key].reconnect_lock.locked():
                self._ws_clients[key].reconnect_lock.release()
            self._ws_clients[key].reconnect_count = 0
            if self._ws_clients[key].client:
                curr_ws_id = self._ws_clients[key].ws_id
                self._logger.info(f"Close {key} websocket connection (id={curr_ws_id}) to infinity Exchange")
                self._ws_clients[key].client.close()

    @staticmethod
    def create_subscription_message(channel_str: str) -> dict:
        """
        Create subscribe message.

        Args:
            channel_str (str): Channel name

        Returns:
            dict: Subscribe message
        """
        return {
            "method": "SUBSCRIBE",
            "params": [
                channel_str
            ]
        }

    @staticmethod
    def create_unsubscription_message(channel_str: str) -> dict:
        """
        Create unsubscribe message.

        Args:
            channel_str (str): Channel name to unsubscribe from

        Returns:
            dict: Unsubscribe message
        """
        return {
            "method": "UNSUBSCRIBE",
            "params": [
                channel_str
            ]
        }

    def send_message(self, message: dict, is_private: bool = False) -> None:
        """
        Sends a message using the public websocket.

        Args:
            message (str): The message to be sent.
            is_private(bool): a flag to determine message send to which websocket. Default (False) to send to public ws.

        Returns:
            None
        """
        key = "private" if is_private else "public"
        message["id"] = self._ws_clients[key].request_id
        self._logger.debug(f"Sending websocket {key} message {message=}.")
        if self._ws_clients[key].client:
            self._ws_clients[key].client.send(json.dumps(message))
            self._ws_clients[key].request_id += 1

    def get_subscription(self, is_private: bool = False) -> None:
        """
        Get subscribed channels

        Args:
            is_private(bool): a flag to determine message send to which websocket. Default (False) to send to public ws.
        """
        message = {
            "method": "LIST_SUBSCRIPTIONS"
        }
        self.send_message(message=message, is_private=is_private)

    def get_received_data(self, channel: str) -> dict:
        """
        Retrieves the received data from the subscribed channel.

        Args:
            channel (str): The name of the channel.

        Returns:
            str: The received message.
        """
        if len(self._subscribed_data_dict[channel]) > 0:
            message = self._subscribed_data_dict[channel].popleft()
            return message

    def private_ws_login(self) -> None:
        """
        Send ws login to private websocket session

        Returns:
            None
        """
        login_message = {
            "method": "LOGIN",
            "params": {
                "accessToken": self._inf_login.get_access_token()
            }
        }
        self._logger.debug(f"Private websocket login {login_message=}.")
        # do on private session
        self.send_message(message=login_message, is_private=True)

    def subscribe_orderbook(self, instrument_id: str) -> None:
        """
        Subscribes to the order book channel for a given instrument id.

        Args:
            instrument_id (str): The instrument id of the market (e.g. ETH-SPOT).

        Returns:
            None
        """
        channel_str = self.generate_param_str(instrument_id=instrument_id, channel=constants.CHANNEL_ORDER_BOOK)
        message = self.create_subscription_message(channel_str=channel_str)
        self._logger.debug(f"Subscribing orderbook for {instrument_id=}, {channel_str=}, {message=}.")
        self.send_message(message=message, is_private=False)

    def unsubscribe_orderbook(self, instrument_id: str) -> None:
        """
        Unsubscribes from the order book channel for a given instrument id.

        Args:
            instrument_id (str): The instrument id of the market (e.g. ETH-SPOT).

        Returns:
            None
        """
        channel_str = self.generate_param_str(instrument_id=instrument_id, channel=constants.CHANNEL_ORDER_BOOK)
        message = self.create_unsubscription_message(channel_str=channel_str)
        self._logger.debug(f"Unsubscribing orderbook for {instrument_id=}, {channel_str=}, {message=}.")
        self.send_message(message=message, is_private=False)

    def subscribe_public_trades(self, instrument_id: str) -> None:
        """
        Subscribes to the public trades channel for a given instrument id.

        Args:
            instrument_id (str): The instrument id of the market (e.g. ETH-SPOT).

        Returns:
            None
        """
        channel_str = self.generate_param_str(instrument_id=instrument_id, channel=constants.CHANNEL_RECENT_TRADES)
        message = self.create_subscription_message(channel_str=channel_str)
        self._logger.debug(f"Subscribing public trades channel for {instrument_id=}, {channel_str=}, {message=}.")
        self.send_message(message=message, is_private=False)

    def unsubscribe_public_trades(self, instrument_id: str) -> None:
        """
        Unsubscribes from the public trades channel for a given instrument id.

        Args:
            instrument_id (str): The instrument id of the market (e.g. ETH-SPOT).

        Returns:
            None
        """
        channel_str = self.generate_param_str(instrument_id=instrument_id, channel=constants.CHANNEL_RECENT_TRADES)
        message = self.create_unsubscription_message(channel_str=channel_str)
        self._logger.debug(f"Unsubscribing public trades channel for {instrument_id=}, {channel_str=}, {message=}.")
        self.send_message(message=message, is_private=False)

    def subscribe_user_trade(self, instrument_id: str) -> None:
        """
        Subscribes to the user trade channel for a given instrument id.
        This function is a private function that requires infinity login.

        Args:
            instrument_id (str): The instrument id of the market (e.g. ETH-SPOT).

        Returns:
            None
        """
        channel_str = self.generate_param_str(instrument_id=instrument_id, channel=constants.CHANNEL_USER_TRADE)
        message = self.create_subscription_message(channel_str=channel_str)
        self._logger.debug(f"Subscribing user trade channel for {instrument_id=}, {channel_str=}, {message=}.")
        self.send_message(message=message, is_private=True)

    def unsubscribe_user_trade(self, instrument_id: str) -> None:
        """
        Unsubscribes from the user trade channel for a given instrument id.
        This function is a private function that requires infinity login.

        Args:
            instrument_id (str): The instrument id of the market (e.g. ETH-SPOT).

        Returns:
            None
        """
        channel_str = self.generate_param_str(instrument_id=instrument_id, channel=constants.CHANNEL_USER_TRADE)
        message = self.create_unsubscription_message(channel_str=channel_str)
        self._logger.debug(f"Unsubscribing user trade channel for {instrument_id=}, {channel_str=}, {message=}.")
        self.send_message(message=message, is_private=True)

    def subscribe_user_order(self, instrument_id: str) -> None:
        """
        Subscribes to the user order channel for a given instrument id.
        This function is a private function that requires infinity login.

        Args:
            instrument_id (str): The instrument id of the market (e.g. ETH-SPOT).

        Returns:
            None
        """
        channel_str = self.generate_param_str(instrument_id=instrument_id, channel=constants.CHANNEL_USER_ORDER)
        message = self.create_subscription_message(channel_str=channel_str)
        self._logger.debug(f"Subscribing user order channel for {instrument_id=}, {channel_str=}, {message=}.")
        self.send_message(message=message, is_private=True)

    def unsubscribe_user_order(self, instrument_id: str) -> None:
        """
        Unsubscribes from the user order channel for a given instrument id.
        This function is a private function that requires infinity login.

        Args:
            instrument_id (str): The instrument id of the market (e.g. ETH-SPOT).

        Returns:
            None
        """
        channel_str = self.generate_param_str(instrument_id=instrument_id, channel=constants.CHANNEL_USER_ORDER)
        message = self.create_unsubscription_message(channel_str=channel_str)
        self._logger.debug(f"Unsubscribing user order channel for {instrument_id=}, {channel_str=}, {message=}.")
        self.send_message(message=message, is_private=True)

    @staticmethod
    def generate_param_str(instrument_id: str, channel: str) -> str:
        """
        Generate the channel parameter for a websocket subscription or un-subscription.

        Args:
            instrument_id (str): The instrument id for which the subscription is being made.
            channel (str): The channel for the subscription.

        Returns:
            str: The string representation of the channel parameter.
        """
        return f"{instrument_id}@{channel}"

    def on_orderbook_data(self, message: dict) -> None:
        """
        Process the orderbook data received from the WebSocket connection.

        Args:
            message (dict): The orderbook data received from the WebSocket connection.

        Returns:
            None

        Example:
            {
                "e": "orderBook",  # Channel name
                "E": 1696584283888,
                "s": "ETH-2023-10-07",  # Market name
                "m": 10358,  # Market id
                "P": {
                    "a": [  # Asks
                        {
                            "p": "0.0351",  # Rate
                            "q": "3.8105"  # Quantity
                        },
                        ...
                    ],
                    "b": [  # Bids
                        {
                            "p": "0.0319",
                            "q": "3.8786"
                        },
                        ...
                    ]
                }
            }
        """
        try:
            instrument_id = message.get("I", None) if message.get("I", None) is not None else message.get("s", None)
            update_time = None
            if message.get("E", None) is not None:
                update_time = datetime.utcfromtimestamp(message.get("E") / 1000)

            price_dict = message.get("P", {})

            asks_list = price_dict.get("a", [])
            bids_list = price_dict.get("b", [])

            asks_book = {float(price_obj.get("p", 0)): float(price_obj.get("q", 0)) for price_obj in asks_list}
            asks_book = {k: asks_book[k] for k in sorted(asks_book, reverse=True)}

            bids_book = {float(price_obj.get("p", 0)): float(price_obj.get("q", 0)) for price_obj in bids_list}
            bids_book = {k: bids_book[k] for k in sorted(bids_book)}

            book = {constants.INSTRUMENT_ID: instrument_id, constants.UPDATE_TIME: update_time,
                    constants.BIDS: bids_book, constants.ASKS: asks_book}

            self._logger.debug(f"Orderbook: {book=}.")
            self.process_orderbook_data(orderbook=book)
        except Exception as e:
            self._logger.error(f"Exception thrown in on_orderbook_data raw={message}, {e=}. {traceback.format_exc()}")

    def process_orderbook_data(self, orderbook: dict) -> None:
        """
        Process orderbook data.

        Args:
            orderbook (dict): The orderbook data to be processed.

        Returns:
            None
        """
        self._subscribed_data_dict[constants.CHANNEL_ORDER_BOOK].append(orderbook)

    def on_user_trade_data(self, message: dict) -> None:
        """
        Process user trade data received from the WebSocket connection.

        Args: message (dict): The user trade data received from the WebSocket connection.

        Returns:
            None

        Example of user trade raw message:
        {
            "e": "userTrade",
            "E": 1696384117706,
            "s": "ETH-SPOT",
            "m": 1,
            "P": {
                "p": "0.011", (price)
                "q": "0.0074", (quantity)
                "d": 1696384117681, (trade time)
                "t": 38088018, (trade ID)
                "w": 207, (account ID)
                "s": false, (side, True is borrow and False is LEND)
                "o": 54683065 (order ID)
            }
        }
        """
        try:
            symbol = message.get("s", None)
            # private message object
            message = message.get("P", {})
            instrument_id = message.get("I", None) if message.get("I", None) is not None else symbol
            trade_id = message.get("t", None)
            order_id = message.get("o", None)
            account_id = message.get("w", None)
            rate = float(message.get("p", 0))
            quantity = float(message.get("q", 0))
            side = constants.BORROW if message.get("s", None) else constants.LEND
            trade_time = None
            if message.get("d", None) is not None:
                trade_time = datetime.utcfromtimestamp(message.get("d") / 1000)
            user_trade = {
                constants.INSTRUMENT_ID: instrument_id,
                constants.TRADE_ID: trade_id,
                constants.ORDER_ID: order_id,
                constants.ACCOUNT_ID: account_id,
                constants.SIDE: side,
                constants.RATE: rate,
                constants.QUANTITY: quantity,
                constants.TRADE_TIME: trade_time
            }

            self._logger.debug(f"User trade: {user_trade=}.")
            self.process_user_trade(user_trade=user_trade)
        except Exception as e:
            self._logger.error(f"Exception thrown in on_user_trades raw={message}, {e=}. {traceback.format_exc()}")

    def process_user_trade(self, user_trade: dict) -> None:
        """
        Process user trade data.

        Args:
            user_trade (dict): The user trade data to be processed.

        Returns:
            None
        """
        self._subscribed_data_dict[constants.CHANNEL_USER_TRADE].append(user_trade)

    def on_user_order_data(self, message: dict) -> None:
        """
        Process user order data received from the WebSocket connection.

        Args: message (dict): The user order data received from the WebSocket connection.

        Returns:
            None

        Example of user order:
        {
            "e": "userOrder",
            "E": 1696384117706,
            "s": "ETH-SPOT", (symbol)
            "m": 1, (market ID)
            "P": {
                "I": "ETH-SPOT", (instrument ID)
                "m": 1, (market ID)
                "p": "0.01", (price)
                "q": "0.01", (quantity)
                "a": "0.01", (accumulated filled size)
                "d": 1696384117635, (create timestamp)
                "w": 207, (account ID)
                "s": false, (side, True as borrow and False as LEND)
                "i": "f85f64d7", (client order ID)
                "o": 54683065, (order ID)
                "O": 1, (1 as market order and 2 as limit order)
                "M": 1, (1 as floating rate order and 2 as fixed rate order)
                "S": 10 (order status)
            }
        }
        """
        try:
            symbol = message.get("s", None)
            # private message object
            message = message.get("P", {})
            order_id = message.get("o", None)
            client_order_id = message.get("i", None)
            order_type = None
            if message.get("O", None) is not None:
                order_type = constants.LIMIT_ORDER if int(message.get("O")) == 2 else constants.MARKET_ORDER
            account_id = message.get("w", None)
            instrument_id = message.get("I", None) if message.get("I", None) is not None else symbol
            market_type = None
            if message.get("M", None) is not None:
                market_type = constants.FLOATING if int(message.get("M")) == 1 else constants.FIXED_RATE
            quantity = float(message.get("q", 0))
            side = constants.BORROW if message.get("s", None) else constants.LEND
            acc_fill_size = float(message.get("a", 0))
            create_date = None
            if message.get("d", None) is not None:
                create_date = datetime.utcfromtimestamp(message.get("d") / 1000)
            order_status = None
            if message.get("S", None) is not None:
                order_status = int(message.get("S"))
            rate = float(message.get("p", 0))

            user_order = {
                constants.ORDER_ID: order_id,
                constants.CLIENT_ORDER_ID: client_order_id,
                constants.ORDER_TYPE: order_type,
                constants.ACCOUNT_ID: account_id,
                constants.INSTRUMENT_ID: instrument_id,
                constants.MARKET_TYPE: market_type,
                constants.RATE: rate,
                constants.QUANTITY: quantity,
                constants.SIDE: side,
                constants.ACC_FILL_SIZE: acc_fill_size,
                constants.CREATE_TIME: create_date,
                constants.ORDER_STATUS: constants.ORDER_STATUS_TYPE[order_status]
            }
            if message.get("u", None) is not None:
                update_date = datetime.utcfromtimestamp(message.get("u") / 1000)
                user_order[constants.UPDATE_TIME] = update_date
            self._logger.debug(f"User order: {user_order=}.")
            self.process_user_order(user_order=user_order)
        except Exception as e:
            self._logger.error(f"Exception thrown in on_user_orders raw={message}, {e=}. {traceback.format_exc()}")

    def process_user_order(self, user_order: dict) -> None:
        """
        Process user order data.

        Args:
            user_order (dict): The user order data to be processed.

        Returns:
            None
        """
        self._subscribed_data_dict[constants.CHANNEL_USER_ORDER].append(user_order)

    def on_public_trade(self, message: dict) -> None:
        """
        Processes recent trade data received from the WebSocket connection.

        Args: message (dict): The user order data received from the WebSocket connection.

        Returns:
            None

        Example:
        {
            "e": "recentTrades",
            "E": 1702970997315,
            "s": "USDT-2023-12-29",
            "m": 12148,
            "P": [
                {
                    "p": "0.0518",
                    "q": "1353.3",
                    "d": 1702970997296,
                    "s": "True"
                },
                {
                    "p": "0.0514",
                    "q": "4065.21",
                    "d": 1702970997296,
                    "s": "True"
                }
            ]
        }
        """
        try:
            instrument_id = message.get("I") if message.get("I", None) is not None else message.get("s", "")
            splits = instrument_id.split("-")
            if len(splits) == 2 and splits[1] == "SPOT":
                rates_type = constants.FLOATING
            else:
                rates_type = constants.FIXED_RATE
            trades = message.get("P", [])
            if trades is not None and len(trades) > 0:
                for trade_msg in trades:
                    rate = float(trade_msg.get("p", 0))
                    quantity = float(trade_msg.get("q", 0))
                    side = constants.BORROW if trade_msg.get("s", None) else constants.LEND
                    trade_time = datetime.utcfromtimestamp(trade_msg.get("d", None) / 1000)
                    public_trade = {
                        constants.INSTRUMENT_ID: instrument_id,
                        constants.RATES_TYPE: rates_type,
                        constants.TRADE_TIME: trade_time,
                        constants.RATE: rate,
                        constants.QUANTITY: quantity,
                        constants.SIDE: side
                    }
                    self._logger.debug(f"Public trade: {public_trade}.")
                    self.process_public_trade(public_trade=public_trade)
        except Exception as e:
            self._logger.error(f"Exception thrown in on_public_trades raw={message}, {e=}. {traceback.format_exc()}")

    def process_public_trade(self, public_trade: dict) -> None:
        """
        Process a public trade.

        Args:
            public_trade (dict): The trade data received from the websocket.

        Returns:
            None
        """
        self._subscribed_data_dict[constants.CHANNEL_RECENT_TRADES].append(public_trade)

    def on_open(self, ws: websocket.WebSocketApp, ws_id: str) -> None:
        """
        Handle the event when the websocket connection is opened.

        Args:
            ws (websocket.WebSocketApp): websocket app.
            ws_id (str): websocket unique ID.

        Returns:
            None
        """
        is_private = self.is_ws_private(ws_id=ws_id)
        key = "private" if is_private else "public"
        self._logger.debug(f"{key} websocket connection(id={ws_id}) opened")
        if is_private:
            self.private_ws_login()
        else:
            self._ws_clients[key].force_reconnect_event = RepeatTimer(interval=self.__reconnect_interval,
                                                                      function=self.re_connect,
                                                                      args=[is_private])
            self._ws_clients[key].force_reconnect_event.start()
            self._ws_clients[key].is_open = True  # mark public websocket is ready

    def on_message(self, ws: websocket.WebSocketApp, message: str, ws_id: str) -> None:
        """
        Handle the event when a message is received on the websocket.

        Args:
            ws (websocket.WebSocketApp): websocket app
            message (str): The message received from the websocket.
            ws_id (str): websocket unique ID.

        Returns:
            None
        """
        is_private = self.is_ws_private(ws_id=ws_id)
        key = "private" if is_private else "public"
        self._logger.debug(f"Received {key} message on ws(id={ws_id}): {message=}.")
        message_obj = json.loads(message)
        data = message_obj.get("data", {})
        # get private subscriptions
        subscriptions = data.get("subscriptions", None)
        if subscriptions is not None and isinstance(subscriptions, list) and len(subscriptions) > 0:
            self._logger.debug(f"[{ws_id=}] {key} subscription list: {subscriptions}.")
            self._ws_clients[key].subscribed_channels = subscriptions
        # check private websocket login
        if (is_private
                and str(data.get("user", {}).get("address")).casefold() == self._inf_login.account_address.casefold()):
            self._ws_clients[key].force_reconnect_event = RepeatTimer(interval=self.__reconnect_interval,
                                                                      function=self.re_connect,
                                                                      args=[is_private])
            self._ws_clients[key].force_reconnect_event.start()
            self._ws_clients[key].is_open = True  # mark private websocket is ready
            self._logger.info(f"[{ws_id=}] {key} websocket logged in.")

        channel = message_obj.get("e", None)
        if channel is not None:
            if channel == constants.CHANNEL_RECENT_TRADES:
                self.on_public_trade(message=message_obj)
            elif channel == constants.CHANNEL_ORDER_BOOK:
                self.on_orderbook_data(message=message_obj)
            elif channel == constants.CHANNEL_USER_ORDER:
                self.on_user_order_data(message=message_obj)
            elif channel == constants.CHANNEL_USER_TRADE:
                self.on_user_trade_data(message=message_obj)

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, message: str, ws_id: str) -> None:
        """
        Callback function called when a websocket connection is closed.
        If close status code is not normal and reconnection is not already in progress, trigger reconnection.

        Args:
            ws (websocket.WebSocketApp): websocket app
            close_status_code (int): The status code indicating the reason for the closure.
                                    close_status_code 4000 = expires the websocket connection
            message (str): A human-readable string explaining the reason for the closure.
            ws_id (str): websocket unique ID.

        Returns:
            None
        """
        is_private = self.is_ws_private(ws_id=ws_id)
        key = "private" if is_private else "public"
        if (close_status_code is not None and close_status_code != websocket.STATUS_NORMAL
                and not self._ws_clients[key].reconnect_lock.locked()):
            if close_status_code == 4000:
                self._logger.info(
                    f"{key} websocket connection(id={ws_id}) normally closed by Infinity Exchange. {message=}.")
            else:
                self._logger.warning(
                    f"{key} websocket connection(id={ws_id}) unexpected closed [{close_status_code=}]. {message=}.")
                self.re_connect_on_unexpected(is_private=is_private)
        else:
            self._logger.info(f"{key} websocket connection(id={ws_id}) normally closed. {message=}.")
        self._ws_clients[key].is_open = False

    def on_error(self, ws: websocket.WebSocketApp, error, ws_id: str) -> None:
        """
        Callback function called when an error occurs in a websocket connection.

        Args:
            ws (websocket.WebSocketApp): websocket app
            error (Exception): The exception object representing the error.
            ws_id (str): websocket unique ID.

        Returns:
            None
        """
        is_private = self.is_ws_private(ws_id=ws_id)
        key = "private" if is_private else "public"
        if (not self._ws_clients[key].reconnect_lock.locked()
                and isinstance(error, websocket.WebSocketConnectionClosedException)):
            self._logger.warning(f"{key} websocket(id={ws_id}) connection error: {error=}. Trigger reconnection.")
            self.re_connect_on_unexpected(is_private=is_private)

    def on_ping(self, ws: websocket.WebSocketApp, message: str, ws_id: str) -> None:
        """
        Callback function called when a ping message is received.

        Args:
            ws (websocket.WebSocketApp): websocket app
            message (str): The ping message received from the server.
            ws_id (str): websocket unique ID.

        Returns:
            None
        """
        is_private = self.is_ws_private(ws_id=ws_id)
        key = "private" if is_private else "public"
        self._logger.debug(f"{key} websocket(id={ws_id}) got ping, reply sent.")

    def on_pong(self, ws: websocket.WebSocketApp, message: str, ws_id: str) -> None:
        """
        Callback function called when a pong message is received.

        Args:
            ws (websocket.WebSocketApp): websocket app
            message (str): The pong message received from the server.
            ws_id (str): websocket unique ID.

        Returns:
            None
        """
        is_private = self.is_ws_private(ws_id=ws_id)
        key = "private" if is_private else "public"
        self._logger.debug(f"{key} websocket(id={ws_id}) got pong, no need to reply.")

    def is_ws_private(self, ws_id: str) -> bool:
        """
        Check websocket unique ID and determine whether is private websocket

        Args:
            ws_id (str): websocket unique ID.

        Returns:
            bool
        """
        if self._ws_clients["private"].ws_id == ws_id:
            return True
        elif self._ws_clients["public"].ws_id == ws_id:
            return False
        else:
            self._logger.error(f"cannot identity websocket ID({ws_id}), trace={traceback.format_exc()}")
            return False
