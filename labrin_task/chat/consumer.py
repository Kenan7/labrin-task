import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q

from labrin_task.fileapp.models import FileModel

from .models import ChatMessages

User = get_user_model()


import logging as log


class ChatConsumer(WebsocketConsumer):
    # this is a simple local cache that is holding frequent users in memory,
    # because we will need to look up author of every message to store it in the database
    # we are speeding up that process so we don't hit up the database for every new message
    frequent_users = {}

    def fetch_messages(self, data=None):
        self.filemodel_object = FileModel.objects.get(id=self.room_name)
        messages = self.filemodel_object.messages.all()
        if len(messages) == 0:
            content = {
                "command": "empty",
            }
        else:
            content = {
                "command": "messages",
                "messages": self.messages_to_json(messages),
            }
        self.send_message(content)

    def fetch_all_after_delete(self, data=None):
        self.filemodel_object = FileModel.objects.get(id=self.room_name)
        messages = self.filemodel_object.messages.all()

        if len(messages) == 0:
            content = {
                "command": "empty",
            }
        else:
            content = {
                "command": "messages",
                "messages": self.messages_to_json(messages),
            }
        self.send_chat_message_with_type(
            "messages", self.messages_to_json(messages)
        )

    def delete_message(self, message):
        # let's check if you are really the owner
        if self.scope.get("user", "none") == self.filemodel_object.owner:
            try:
                self.filemodel_object.messages.get(message["message"]).delete()
            except:
                # we cache again
                self.filemodel_object = FileModel.objects.get(
                    id=self.room_name
                )
                self.filemodel_object.messages.get(
                    id=message["message"]
                ).delete()

                self.fetch_all_after_delete()
            finally:
                pass

    def delete_all_messages(self, message):
        # let's check if you are really the owner
        if self.scope.get("user", "none") == self.filemodel_object.owner:
            try:
                self.filemodel_object = FileModel.objects.get(
                    id=self.room_name
                )
                log.info(self.filemodel_object.messages.delete())

            except:
                pass

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        try:
            author = message.author.username

        except:
            author = "<deleted_user>"
        return {
            "author": author,
            "text": message.text,
            "id": message.id,
            "created_at": str(message.created_at.strftime("%H:%M")),
        }

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    def send_chat_message_with_type(self, command, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": command, "message": message}
        )

    def new_message(self, message):
        if (
            self.scope.get("user", None)
            in self.filemodel_object.commenters.all()
        ):

            author = message["from"]
            if author in self.frequent_users:
                user = self.frequent_users[author]
            else:
                user = User.objects.get(username=author)
                self.frequent_users[author] = user

            new_created_message = self.filemodel_object.messages.create(
                text=message["message"], author=user
            )

            content = {
                "command": "new_message",
                "message": self.message_to_json(new_created_message),
            }
            return self.send_chat_message(content)

        else:
            log.info("wait.. how did you get here?!")
            log.info(self.scope)

    # Receive message from WebSocket
    def receive(self, text_data):
        try:
            if self.scope["user"] in self.filemodel_object.commenters.all():
                text_data_json = json.loads(text_data)
                self.commands[text_data_json["command"]](self, text_data_json)
        except:
            # we could also save it to second db, but with apps like logdna, we will access this logs anyway
            log.info(f"let's see what happened here.. {self.scope}")
        finally:
            pass

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # we are storing the fileobject that we are in the chat of so we can access faster
        self.filemodel_object = FileModel.objects.get(id=self.room_name)

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

    commands = {
        "fetch_messages": fetch_messages,
        "new_message": new_message,
        "delete_message": delete_message,
        "delete_all_messages": delete_all_messages,
    }
