from uuid import uuid4

from django.db import models
from django.utils import timezone


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class CreateDateModel(models.Model):
    create_date = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class ModifyDateModel(models.Model):
    modify_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
