import pytest
import factory

from rest_framework.test import APIClient
from rest_framework import status

from .factory import UserFactory, UserFriendshipFactory
from user.constants import UserFriendshipState


@pytest.fixture
def user_1():
    return UserFactory(username='user_1')


@pytest.fixture
def user_2():
    return UserFactory(username='user_2')

@pytest.mark.django_db
def test_user_friendship_create__ok(user_1, user_2):
    client = APIClient()
    client.force_authenticate(user=user_1)
    
    response = client.post('/api/user/friendship/', data={'receiver_id': user_2.id}, format='json')
    assert response.data.get('sender_id') == user_1.id
    assert response.data.get('receiver_id') == user_2.id
    assert response.data.get('state') == UserFriendshipState.REQUESTED


@pytest.mark.django_db
def test_user_friendship_create_to_himself(user_1, user_2):
    client = APIClient()
    client.force_authenticate(user=user_1)
    
    response = client.post('/api/user/friendship/', data={'receiver_id': user_1.id}, format='json')
    print(response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST