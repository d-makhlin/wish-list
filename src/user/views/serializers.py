from rest_framework import serializers

from user.constants import UserFriendshipState
from user.models import User
from user.models.userfriendship import UserFriendship


class UserFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFriendship
        fields = ('id', 'sender_id', 'receiver_id', 'state')


class UserFriendCreateSerializer(serializers.Serializer):
    receiver_id = serializers.UUIDField(required=True)


class UserFriendSerializerList(serializers.Serializer):
    state = serializers.ChoiceField(choices=UserFriendshipState)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class UserFindSerializer(serializers.Serializer):
    pattern = serializers.CharField(required=True)
