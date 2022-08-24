from typing import Any
from uuid import UUID

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from user.constants import UserFriendshipState
from user.models import User
from user.models.userfriendship import UserFriendship
from user.services.user_friendship_service import UserFriendshipService
from user.views.serializers import UserFriendSerializer, UserFriendCreateSerializer, UserFriendSerializerList


class UserFriendshipView(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserFriendSerializer
    queryset = UserFriendship.objects.all()

    def retrieve(self, request: Request, pk: UUID) -> Response:
        friendship = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(friendship)
        return Response(serializer.data)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = UserFriendCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if request.user.id == validated_data['receiver_id']:
            return Response(status=status.HTTP_400_BAD_REQUEST)  # ToDo implement errors

        user_friendship = UserFriendshipService.create_user_friendship(
            sender=User.objects.get(pk=request.user.id),
            receiver=User.objects.get(pk=validated_data['receiver_id']),
        )
        serializer = self.serializer_class(user_friendship)
        return Response(serializer.data)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = UserFriendSerializerList(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        serializer = self.serializer_class(
            UserFriendshipService.get_user_friendships_by_state(
                user_id=request.user.id, state=validated_data.get('state')
            ),
            many=True,
        )
        return Response(serializer.data)

    @action(methods=('post',), detail=True, url_path='accept')
    def accept(self, request: Request, pk: str) -> Response:
        user_friendship = get_object_or_404(
            self.queryset.filter(receiver_id=request.user.id, state=UserFriendshipState.REQUESTED), pk=pk
        )
        instance = UserFriendshipService.accept_friendship_request(user_friendship)
        return Response(self.serializer_class(instance).data)

    @action(methods=('post',), detail=True, url_path='reject')
    def reject(self, request: Request, pk: str) -> Response:
        user_friendship = get_object_or_404(
            self.queryset.filter(receiver_id=request.user.id, state=UserFriendshipState.REQUESTED), pk=pk
        )
        instance = UserFriendshipService.reject_friendship_request(user_friendship)
        return Response(self.serializer_class(instance).data)
