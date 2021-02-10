from django.contrib.auth import get_user_model
from django.db.models import CASCADE, SET_NULL, CharField, ForeignKey

from labrin_task.common import TimeStampedModel
from labrin_task.fileapp.models import FileModel

User = get_user_model()


class ChatMessages(TimeStampedModel):
    text = CharField(max_length=100)

    author = ForeignKey(
        User, related_name="author", on_delete=SET_NULL, null=True
    )

    file_messages = ForeignKey(
        FileModel, related_name="messages", on_delete=CASCADE
    )
