from django.db.models import CASCADE, CharField, ForeignKey, Model


class ChatMessages(Model):
    text = CharField(max_length=100)
    file_messages = ForeignKey(
        "FileModel", related_name="messages", on_delete=CASCADE
    )
