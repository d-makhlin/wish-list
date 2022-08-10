from django.db import models

from common.models import UUIDModel, CreateDateModel, ModifyDateModel


class WishList(UUIDModel, CreateDateModel, ModifyDateModel):
    name = models.TextField(blank=True)
    owner = models.ForeignKey('user.User', models.CASCADE)
