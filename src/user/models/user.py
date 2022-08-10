from django.contrib.auth.models import User as BaseUser

from django.db import models

from common.fields import EnumField
from user.constants import UserStatus


class User(BaseUser):
    Status = UserStatus

    phone_no = models.CharField(max_length=20)
    photo = models.ImageField(blank=True, null=True)

    status = EnumField(UserStatus, default=UserStatus.ACTIVE)
