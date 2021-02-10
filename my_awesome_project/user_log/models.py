from django.db.models import SET_NULL, CharField, OneToOneField
from django.db.models.base import Model

from my_awesome_project.common import TimeStampedModel

from .parser import InformationParser

NULL_AND_BLANK = {"null": True, "blank": True}


class UserLogOSModel(Model):
    os_name = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )
    os_family = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )
    os_version = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )


class UserLogBrowserModel(Model):
    browser_name = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )
    browser_family = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )
    browser_version = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )


class UserLogDeviceModel(Model):
    device_name = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )
    device_family = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )


class UserLoggerModel(TimeStampedModel):
    # created_at is kind of login_time
    user_agent = CharField(
        max_length=100,
        **NULL_AND_BLANK,
    )
    browser = OneToOneField(
        UserLogBrowserModel,
        on_delete=SET_NULL,
        **NULL_AND_BLANK,
    )
    operating_system = OneToOneField(
        UserLogOSModel,
        on_delete=SET_NULL,
        **NULL_AND_BLANK,
    )
    device = OneToOneField(
        UserLogDeviceModel,
        on_delete=SET_NULL,
        **NULL_AND_BLANK,
    )

    # intentionally used charfield not ipaddressfield
    ip_address = CharField(
        max_length=60,
        **NULL_AND_BLANK,
    )

    def get_info_from_parser(self):
        info = InformationParser(self.user_agent)
