import uuid
from django.contrib.auth.models import AbstractUser

from django.db import models

from common.fields import EnumField
from user.constants import UserStatus


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Status = UserStatus

    phone_no = models.CharField(max_length=20)
    photo = models.ImageField(blank=True, null=True)

    status = EnumField(UserStatus, default=UserStatus.ACTIVE)
