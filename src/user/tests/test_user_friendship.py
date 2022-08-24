import pytest

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
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_user_friendship_accept(user_1, user_2):
    user_friendship = UserFriendshipFactory(sender=user_1, receiver=user_2)
    client = APIClient()
    client.force_authenticate(user=user_2)
    assert user_friendship.state == UserFriendshipState.REQUESTED
    
    response = client.post(f'/api/user/friendship/{user_friendship.id}/accept/')
    assert response.data.get('id') == str(user_friendship.id)
    assert response.data.get('sender_id') == user_1.id
    assert response.data.get('receiver_id') == user_2.id
    assert response.data.get('state') == UserFriendshipState.ACCEPTED

@pytest.mark.django_db
def test_user_friendship_accept_wrong_state(user_1, user_2):
    user_friendship = UserFriendshipFactory(sender=user_1, receiver=user_2, state=UserFriendshipState.ACCEPTED)
    client = APIClient()
    client.force_authenticate(user=user_2)
    
    response = client.post(f'/api/user/friendship/{user_friendship.id}/accept/')
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_user_friendship_reject(user_1, user_2):
    user_friendship = UserFriendshipFactory(sender=user_1, receiver=user_2)
    client = APIClient()
    client.force_authenticate(user=user_2)
    assert user_friendship.state == UserFriendshipState.REQUESTED
    
    response = client.post(f'/api/user/friendship/{user_friendship.id}/reject/')
    assert response.data.get('id') == str(user_friendship.id)
    assert response.data.get('sender_id') == user_1.id
    assert response.data.get('receiver_id') == user_2.id
    assert response.data.get('state') == UserFriendshipState.REJECTED

@pytest.mark.django_db
def test_user_friendship_reject_wrong_state(user_1, user_2):
    user_friendship = UserFriendshipFactory(sender=user_1, receiver=user_2, state=UserFriendshipState.ACCEPTED)
    client = APIClient()
    client.force_authenticate(user=user_2)
    
    response = client.post(('/api/user/friendship/reject/', user_friendship.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
@pytest.mark.parametrize('state, number', [(UserFriendshipState.ACCEPTED, 2), (UserFriendshipState.REQUESTED, 1)])
def test_user_friendship_list(state, number, user_1, user_2):
    UserFriendshipFactory(sender=user_1, receiver=user_2, state=UserFriendshipState.ACCEPTED)

    user_3 = UserFactory(username='user_3')
    UserFriendshipFactory(sender=user_3, receiver=user_1, state=UserFriendshipState.ACCEPTED)

    user_4 = UserFactory(username='user_4')
    UserFriendshipFactory(sender=user_4, receiver=user_1)

    user_5 = UserFactory(username='user_5')
    UserFriendshipFactory(sender=user_1, receiver=user_5)

    client = APIClient()
    client.force_authenticate(user=user_1)
    response = client.get('/api/user/friendship/', {'state': state}, format='json')
    assert len(response.data) == number
