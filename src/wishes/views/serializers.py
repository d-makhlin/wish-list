from typing import Dict, Any

from rest_framework import serializers

from wishes.constants import WishItemStatus
from wishes.models import WishItem, WishList


class WishItemSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()

    class Meta:
        model = WishItem
        fields = ('id', 'name', 'comment', 'due_date', 'list_id', 'state', 'show_gifter_name', 'to_be_gifted_by_id')

    def get_state(self, obj: WishItem) -> WishItemStatus:
        if obj.state in (WishItemStatus.OPEN, WishItemStatus.GIFTED):
            return obj.state
        return WishItemStatus.OPEN if self.context['is_owner'] else obj.state


class WishItemCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    comment = serializers.CharField(required=False, allow_null=True)
    list_id = serializers.UUIDField(required=True)
    due_date = serializers.DateField(required=False)


class WishListSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = WishList
        fields = ('id', 'name', 'owner_id', 'items')

    def get_items(self, obj: WishList) -> Dict[str, Any]:
        return WishItemSerializer(obj.items.all(), many=True).data


class WishListCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)


class WishListSerializerList(serializers.Serializer):
    owner_id = serializers.CharField(required=True)


class WishListSerializerRaw(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ('id', 'name', 'owner_id',)


class WishItemMarkToGiftSerializer(serializers.Serializer):
    show_gifter_name = serializers.BooleanField(required=True)
