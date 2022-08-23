from common.base import BaseFactory
from user.models import User, UserFriendship


class UserFactory(BaseFactory):
    class Meta:
        model = User


class UserFriendshipFactory(BaseFactory):
    class Meta:
        model = UserFriendship
