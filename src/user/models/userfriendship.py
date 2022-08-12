from django.db import models

from common.fields import EnumField
from common.models import UUIDModel, CreateDateModel, ModifyDateModel
from user.constants import UserFriendshipState


class UserFriendship(UUIDModel, CreateDateModel, ModifyDateModel):
    sender = models.ForeignKey('user.User', models.CASCADE, related_name='receivers')
    receiver = models.ForeignKey('user.User', models.CASCADE, related_name='senders')
    state = EnumField(UserFriendshipState, default=UserFriendshipState.REQUESTED)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sender_id', 'receiver_id'], name='exclusive friendship request')
        ]
