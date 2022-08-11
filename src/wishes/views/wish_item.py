from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from wishes.models import WishItem, WishList
from wishes.services.wish_item_service import WishItemService
from wishes.views.serializers import WishItemSerializer, WishItemCreateSerializer


class WishItemView(ModelViewSet):
    serializer_class = WishItemSerializer
    queryset = WishItem.objects.all()

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        wish_item = self.get_object()
        is_owner = request.user.id == wish_item.list.owner_id
        # ToDo check if friends
        serializer = self.serializer_class(wish_item, context={'is_owner': is_owner})
        return Response(serializer.data)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = WishItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        wish_list = get_object_or_404(WishList, pk=validated_data.get('list_id'))
        if wish_list.owner_id != request.user.id:
            return Response({'detail: invalid user'})  # ToDo raise exception

        wish_item = WishItemService.create_wish_item(
            wish_list=wish_list,
            name=validated_data['name'],
            comment=validated_data.get('comment'),
            due_date=validated_data.get('due_date'),
        )
        serializer = self.serializer_class(wish_item, context={'is_owner': True})
        return Response(serializer.data)


