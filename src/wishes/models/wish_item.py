from django.db import models

from common.fields import EnumField
from common.models import UUIDModel, CreateDateModel, ModifyDateModel
from wishes.constants import WishItemStatus


class WishItem(UUIDModel, CreateDateModel, ModifyDateModel):
    name = models.TextField(blank=True)
    comment = models.TextField(blank=True, null=True)
    list = models.ForeignKey('wishes.WishList', models.CASCADE, related_name='items')
    due_date = models.DateField(null=True, blank=True)
    state = EnumField(WishItemStatus, default=WishItemStatus.OPEN)
    to_be_gifted_by = models.ForeignKey('user.User', models.CASCADE, blank=True, null=True)
    show_gifter_name = models.BooleanField(default=True)
