from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from user.models import User
from user.services.user_friendship_service import UserFriendshipService
from wishes.models import WishItem, WishList
from wishes.services.wish_item_service import WishItemService
from wishes.views.serializers import WishItemSerializer, WishItemCreateSerializer, WishItemMarkToGiftSerializer


class WishItemView(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WishItemSerializer
    queryset = WishItem.objects.all()

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        wish_item = self.get_object()
        is_owner = request.user.id == wish_item.list.owner_id
        if not is_owner and not UserFriendshipService.is_in_friendship(request.user.id, wish_item.list.owner_id):
            return Response(status=status.HTTP_400_BAD_REQUEST)  # ToDo raise exception

        serializer = self.serializer_class(wish_item, context={'is_owner': is_owner})
        return Response(serializer.data)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = WishItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        wish_list = get_object_or_404(WishList, pk=validated_data.get('list_id'))
        if wish_list.owner_id != request.user.id:
            return Response({'detail: invalid user'}, status=status.HTTP_400_BAD_REQUEST)  # ToDo raise exception

        wish_item = WishItemService.create_wish_item(
            wish_list=wish_list,
            name=validated_data['name'],
            comment=validated_data.get('comment'),
            due_date=validated_data.get('due_date'),
        )
        serializer = self.serializer_class(wish_item, context={'is_owner': True})
        return Response(serializer.data)

    @action(methods=('post',), detail=True, url_path='mark-to-gift')
    def mark_to_gift(self, request: Request, pk: str) -> Response:
        serializer = WishItemMarkToGiftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        item = get_object_or_404(self.queryset, pk=pk)
        user = get_object_or_404(User, pk=request.user.id)
        return (
            Response(status=status.HTTP_200_OK)
            if WishItemService.mark_to_gift(item, user, validated_data['show_gifter_name'])
            else Response(status=status.HTTP_400_BAD_REQUEST)
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.serializer_class(
            WishItemService.get_items_to_gift(request.user.id), context={'is_owner': False}, many=True
        )
        return Response(serializer.data)
