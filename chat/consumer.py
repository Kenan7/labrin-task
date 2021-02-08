import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
    WebsocketConsumer,
)
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q

from my_awesome_project.fileapp.models import FileModel

User = get_user_model()


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
    # this is a simple local cache that is holding frequent users in memory,
    # because we will need to look up author of every message to store it in the database
    # we are speeding up that process so we don't hit up the database for every new message
    frequent_users = {}

    def fetch_messages(self, data):
        filemodel_object = FileModel.objects.get(id=self.room_name)
        messages = filemodel_object.messages.all()
        content = {
            "command": "messages",
            "messages": self.messages_to_json(messages),
        }
        self.send_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            "author": message.author.username,
            "text": message.text,
            "created_at": str(message.created_at),
        }

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    def new_message(self, message):
        # Send message to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name, {"type": "chat_message", "message": message}
        # )

        author = message["from"]
        if author in self.frequent_users:
            user = self.frequent_users[author]
        else:
            user = User.objects.get(username=author)
            self.frequent_users[author] = user

        new_created_message = self.file_object.messages.create(
            text=message["message"], author=user
        )

        content = {
            "command": "new_message",
            "message": self.message_to_json(new_created_message),
        }
        return self.send_chat_message(content)

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.commands[text_data_json["command"]](self, text_data_json)

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # we are storing the fileobject that we are in the chat of so we can access faster
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

    commands = {"fetch_messages": fetch_messages, "new_message": new_message}
