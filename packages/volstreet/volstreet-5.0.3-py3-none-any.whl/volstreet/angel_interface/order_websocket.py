import json
from volstreet.angel_interface.base_websocket import BaseWebsocket


class OrderWebsocket(BaseWebsocket):
    def __init__(self, auth_token, api_key, client_code, feed_token, manager):
        super().__init__(auth_token, api_key, client_code, feed_token, manager)
        self.command_queue = manager.Queue()

    @property
    def root_uri(self):
        return "wss://tns.angelone.in/smart-order-update"

    @property
    def heart_beat_interval(self):
        return 10

    @property
    def websocket_type(self):
        return "Order websocket"

    def edit_message(self, message):
        # If the message is in bytes, decode it
        if isinstance(message, bytes):
            message = message.decode("utf-8")

        # If the message is a string, parse it as JSON
        if isinstance(message, str):
            message = json.loads(message)
        # Now, access the elements as a dictionary
        order_data = message["orderData"]
        order_id = order_data["orderid"]
        self.data_bank[order_id] = order_data

    def on_data(self, wsapp, message, data_type, continue_flag):
        if data_type == 1 and message != "pong":
            self.edit_message(message)
