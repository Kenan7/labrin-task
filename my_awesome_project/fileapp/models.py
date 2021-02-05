from django.conf import settings
from django.db.models import (
    CASCADE,
    CharField,
    FileField,
    ForeignKey,
    ManyToManyField,
    Model,
)

User = settings.AUTH_USER_MODEL

NULL_AND_BLANK = {"null": True, "blank": True}
BLANK = {"blank": True}
NULL = {"null": True}


class FileModel(Model):
    name = CharField(max_length=20)
    description = CharField(max_length=1000)

    file_itself = FileField(upload_to="files/")

    viewers = ManyToManyField(
        User,
        related_name="viewers",
        **BLANK,
    )
    commenters = ManyToManyField(
        User,
        related_name="commenters",
        **BLANK,
    )

    owner = ForeignKey(User, related_name="owner", on_delete=CASCADE)

    # def get_absolute_url(self):
    #     return reverse("book_detail", args=[self.pk])
