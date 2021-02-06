import logging as log
from datetime import datetime, timedelta

from celery import shared_task
from celery.schedules import crontab
from django.contrib.auth import get_user_model
from django.utils import timezone

from config import celery_app

from .models import FileModel

User = get_user_model()


@shared_task
def delete_old_files():
    """Deleting files older than X days"""
    DAYS = 7

    TODAY = datetime.now(tz=timezone.utc)

    DIFFERENCE = TODAY - timedelta(days=DAYS)

    log.info(f"FROM: {DIFFERENCE} ---> TO: {TODAY}")

    query = FileModel.objects.filter(created_at__lt=DIFFERENCE)

    log.info(f"{len(query)} objects returned from query.")
    log.info(f"The first one is: {query[0].name if len(query) else None}")

    return query.delete()
