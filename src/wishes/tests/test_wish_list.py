import pytest

from rest_framework.test import APIClient
from rest_framework import status
from src.user.constants import UserFriendshipState
from src.user.tests.factory import UserFriendshipFactory
from src.wishes.tests.factory import WishListFactory

from user.tests.factory import UserFactory

@pytest.fixture
def user():
    return UserFactory(username='user')

@pytest.mark.django_db
def test_wish_list_create(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/wishes/wish-list/', data={'name': 'list-1'}, format='json')
    assert response.data.get('owner_id') == user.id
    assert not response.data.get('items')

@pytest.mark.django_db
def test_wish_list_revtrieve__ok(user):
    client = APIClient()
    client.force_authenticate(user=user)

    wish_list = WishListFactory(owner=user)
    response = client.get(f'/api/wishes/wish-list/{wish_list.id}/')
    assert response.data.get('owner_id') == user.id
    assert not response.data.get('items')

@pytest.mark.django_db
def test_wish_list_revtrieve__new_owner(user):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other')
    wish_list = WishListFactory(owner=other_user)
    response = client.get(f'/api/wishes/wish-list/{wish_list.id}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    UserFriendshipFactory(sender=user, receiver=other_user)
    response = client.get(f'/api/wishes/wish-list/{wish_list.id}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_wish_list_revtrieve__friend(user):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other')
    UserFriendshipFactory(sender=user, receiver=other_user, state=UserFriendshipState.ACCEPTED)
    wish_list = WishListFactory(owner=other_user)
    response = client.get(f'/api/wishes/wish-list/{wish_list.id}/')
    assert response.data.get('owner_id') == other_user.id
    assert not response.data.get('items')

@pytest.mark.django_db
def test_wish_list__list(user):
    WishListFactory(owner=user, name='list-1')
    WishListFactory(owner=user, name='list-2')
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/wishes/wish-list/', {'owner_id': user.id}, format='json')
    assert len(response.data) == 2

@pytest.mark.django_db
def test_wish_list__list_new_owner(user):
    other_user = UserFactory(username='other')
    WishListFactory(owner=other_user, name='list-1')
    WishListFactory(owner=other_user, name='list-2')
    
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/wishes/wish-list/', {'owner_id': other_user.id}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_wish_list__list_friend(user):
    other_user = UserFactory(username='other')
    UserFriendshipFactory(sender=user, receiver=other_user, state=UserFriendshipState.ACCEPTED)
    WishListFactory(owner=other_user, name='list-1')
    WishListFactory(owner=other_user, name='list-2')
    
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/wishes/wish-list/', {'owner_id': other_user.id}, format='json')
    assert len(response.data) == 2
