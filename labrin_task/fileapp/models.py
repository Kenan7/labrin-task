# from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE,
    CharField,
    FileField,
    ForeignKey,
    Manager,
    ManyToManyField,
)

from labrin_task.common import TimeStampedModel

User = get_user_model()
# User = settings.AUTH_USER_MODEL

NULL_AND_BLANK = {"null": True, "blank": True}
BLANK = {"blank": True}
NULL = {"null": True}


class FileModelManager(Manager):
    def last_messages(self):
        return self.all().order_by("-id")[:10]

    def owners_all(self, id):
        return self.select_related("owner").filter(owner=id)


class FileModel(TimeStampedModel):
    name = CharField(max_length=20)

    description = CharField(
        max_length=1000, default="default file description"
    )

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

    owner = ForeignKey(User, related_name="owners", on_delete=CASCADE)

    objects = FileModelManager()

    def __str__(self):
        return f"{self.name} - {self.owner.email} - {self.description}"

    # def get_absolute_url(self):
    #     return reverse("book_detail", args=[self.pk])
