import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
    WebsocketConsumer,
)

from my_awesome_project.fileapp.models import FileModel


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "tester_message",
                "tester": "hello world",
            },
        )

    async def tester_message(self, event):
        tester = event["tester"]

        await self.send(
            text_data=json.dumps(
                {
                    "tester": tester,
                }
            )
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        # return super().disconnect(code)


class ChatRoomSyncConsumer(WebsocketConsumer):
    groups = ["broadcast"]

    def connect(self):
        # Called on connection.
        # To accept the connection call:
        self.accept()
        # Or accept the connection and specify a chosen subprotocol.
        # A list of subprotocols specified by the connecting client
        # will be available in self.scope['subprotocols']
        # self.accept("subprotocol")
        # To reject the connection, call:
        # self.close()

    def receive(self, text_data=None, bytes_data=None):
        # Called with either text_data or bytes_data for each frame
        # You can call:
        self.send(text_data="Hello world!")
        # Or, to send a binary frame:
        # self.send(bytes_data="Hello world!")
        # Want to force-close the connection? Call:
        # self.close()
        # Or add a custom WebSocket error code!
        # self.close(code=4123)

    def disconnect(self, close_code):
        pass
        # Called when the socket closes


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # chatinde oldugumuz file obyektini elde edib saxlayiriq ki suretli access ede bilek
        self.file_object = FileModel.objects.get(id=self.room_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

        self.file_object.messages.create(text=message)

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))
