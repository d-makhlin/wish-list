from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from user.models import User
from user.services.user_friendship_service import UserFriendshipService
from wishes.models import WishList
from wishes.services.wish_list_service import WishListService
from wishes.views.serializers import WishListCreateSerializer, WishListSerializer, WishListSerializerList, \
    WishListSerializerRaw


class WishListView(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WishListSerializer
    queryset = WishList.objects.all()

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        wish_list = self.get_object()
        is_owner = request.user.id == wish_list.owner_id
        if not is_owner and not UserFriendshipService.is_in_friendship(request.user.id, wish_list.owner_id):
            return Response(status=status.HTTP_400_BAD_REQUEST)  # ToDo raise exception
        serializer = self.serializer_class(wish_list, context={'is_owner': is_owner})
        return Response(serializer.data)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = WishListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        wish_list = WishListService.create_wish_list(
            user=User.objects.get(pk=request.user.id),
            name=validated_data['name'],
        )
        serializer = self.serializer_class(wish_list)
        return Response(serializer.data)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = WishListSerializerList(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        owner_id = validated_data.get('owner_id')
        is_owner = request.user.id == owner_id
        if not is_owner and not UserFriendshipService.is_in_friendship(request.user.id, owner_id):
            return Response(status=status.HTTP_400_BAD_REQUEST)  # ToDo raise exception

        serializer = WishListSerializerRaw(self.queryset.filter(owner_id=owner_id), many=True)
        return Response(serializer.data)


