from django.db.models import CASCADE, CharField, ForeignKey, Model

from my_awesome_project.fileapp.models import FileModel


class ChatMessages(Model):
    text = CharField(max_length=100)
    file_messages = ForeignKey(
        FileModel, related_name="messages", on_delete=CASCADE
    )
