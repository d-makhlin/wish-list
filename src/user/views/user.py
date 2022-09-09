from typing import Any

from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from user.views.serializers import UserLoginSerializer
from user.forms import UserRegisterForm
from user.models import User
from user.services.user_service import UserService
from user.views.serializers import UserSerializer, UserFindSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UserView(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    @action(methods=('get',), detail=False, url_path='find-user')
    def find_user(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = UserFindSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        queryset = UserService.find_users(
            validated_data['pattern']).order_by('username')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AuthView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=('post',), detail=False, url_path='login')
    def login(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = self.authenticate(email=validated_data.get(
            'email'), password=validated_data.get('password'))
        if user is not None:
            login(request, user)
            return Response(status=status.HTTP_200_OK, data={'user_id': user.id})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @action(methods=('post',), detail=False, url_path='register')
    def register(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        form = UserRegisterForm(request.data)
        if form.is_valid():
            form.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': form.errors})

    def authenticate(self, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return
        except User.MultipleObjectsReturned:
            user = User.objects.filter(email=email).order_by('id').first()
        if user.check_password(password):
            return user
