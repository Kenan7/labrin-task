import time
from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings

from my_awesome_project.fileapp.models import FileModel
from my_awesome_project.fileapp.tasks import delete_old_files

User = get_user_model()


class AddTestCase(TestCase):
    @override_settings(
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_ALWAYS_EAGER=True,
        BROKER_BACKEND="memory",
    )
    def test_delete_old_files(self):
        result = delete_old_files.delay()
        self.assertTrue(result.successful())

    def test_file_creation_viewers_owners_file_deletion(self):
        example_file = SimpleUploadedFile(
            "best_file_eva.txt",
            b"these are the file contents!",
        )

        current_user = User.objects.create(username="test@g.co")
        self.assertEqual("test@g.co", current_user.username)

        today = datetime.now(tz=timezone.utc)

        days_from_now_on = today - timedelta(days=8)

        current_file = FileModel.objects.create(
            name="test.js", file_itself=example_file, owner=current_user
        )

        self.assertEqual("test.js" == current_file.name)

        current_id = current_file.id

        current_file.viewers.set([current_user])
        current_file.commenters.set([current_user])

        self.assertTrue(current_user in current_file.viewers.all())
        self.assertTrue(current_user in current_file.commenters.all())

        current_file.created_at = days_from_now_on
        current_file.save()

        result = delete_old_files.delay()
        self.assertTrue(result.successful())

        self.assertFalse(FileModel.objects.filter(id=current_id).exists())
