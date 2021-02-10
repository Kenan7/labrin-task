import time
from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings

from labrin_task.fileapp.models import FileModel
from labrin_task.fileapp.tasks import delete_old_files

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

        file_should_be_deleted = FileModel.objects.create(
            name="test.js", file_itself=example_file, owner=current_user
        )

        file_should_not_be_deleted = FileModel.objects.create(
            name="main.py", file_itself=example_file, owner=current_user
        )

        self.assertEqual("test.js", file_should_be_deleted.name)

        file_should_be_deleted_id = file_should_be_deleted.id
        file_should_not_be_deleted_id = file_should_not_be_deleted.id

        file_should_be_deleted.viewers.set([current_user])
        file_should_be_deleted.commenters.set([current_user])

        self.assertTrue(current_user in file_should_be_deleted.viewers.all())
        self.assertTrue(
            current_user in file_should_be_deleted.commenters.all()
        )

        file_should_be_deleted.created_at = days_from_now_on
        file_should_be_deleted.save()

        result = delete_old_files.delay()
        self.assertTrue(result.successful())

        self.assertFalse(
            FileModel.objects.filter(id=file_should_be_deleted_id).exists()
        )
        self.assertTrue(
            FileModel.objects.filter(id=file_should_not_be_deleted_id).exists()
        )
