from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user.models import User
from wishes.models import WishList
from wishes.services.wish_list_service import WishListService
from wishes.views.serializers import WishListCreateSerializer, WishListSerializer, WishListSerializerList, \
    WishListSerializerRaw


class WishListView(ModelViewSet):
    serializer_class = WishListSerializer
    queryset = WishList.objects.all()

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        wish_list = self.get_object()
        is_owner = request.user.id == wish_list.owner_id
        # ToDo check if friends
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

        # ToDo check if friends
        serializer = WishListSerializerRaw(self.queryset.filter(owner_id=validated_data.get('owner_id')), many=True)
        return Response(serializer.data)


