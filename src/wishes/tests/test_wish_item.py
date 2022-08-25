import pytest

from rest_framework.test import APIClient
from rest_framework import status
from src.wishes.services.wish_item_service import WishItemService
from src.wishes.tests.factory import WishItemFactory
from user.constants import UserFriendshipState
from user.tests.factory import UserFriendshipFactory
from wishes.tests.factory import WishListFactory
from wishes.constants import WishItemStatus

from user.tests.factory import UserFactory

@pytest.fixture
def user():
    return UserFactory(username='user')

@pytest.mark.django_db
def test_wish_item_create__ok(user):
    client = APIClient()
    client.force_authenticate(user=user)

    wish_list = WishListFactory(name='list-1', owner=user)
    response = client.post('/api/wishes/wish-item/', data={
        'name': 'item-1',
        'comment': None, 
        'due_date': None, 
        'list_id': wish_list.id,
        }, format='json')
    print(response.data)
    assert response.data.get('list_id') == wish_list.id
    assert response.data.get('name') == 'item-1'
    assert response.data.get('state') == WishItemStatus.OPEN

@pytest.mark.django_db
def test_wish_item_create__no_list(user):
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/wishes/wish-item/', data={
        'name': 'item-1',
        'comment': None, 
        'due_date': None, 
        'list_id': '',
        }, format='json')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_wish_item_revtrieve__ok(user):
    client = APIClient()
    client.force_authenticate(user=user)

    wish_list = WishListFactory(owner=user)
    wish_item = WishItemFactory(name='item-1', list=wish_list)
    response = client.get(f'/api/wishes/wish-item/{wish_item.id}/')
    assert response.data.get('list_id') == wish_list.id

@pytest.mark.django_db
def test_wish_item_revtrieve__new_owner(user):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other')
    wish_list = WishListFactory(owner=other_user)
    wish_item = WishItemFactory(name='item-1', list=wish_list)
    response = client.get(f'/api/wishes/wish-item/{wish_item.id}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    UserFriendshipFactory(sender=user, receiver=other_user)
    response = client.get(f'/api/wishes/wish-item/{wish_item.id}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_wish_item_revtrieve__friend(user):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other')
    UserFriendshipFactory(sender=user, receiver=other_user, state=UserFriendshipState.ACCEPTED)
    wish_list = WishListFactory(owner=other_user)
    wish_item = WishItemFactory(name='item-1', list=wish_list)
    response = client.get(f'/api/wishes/wish-item/{wish_item.id}/')
    assert response.data.get('list_id') == wish_list.id


@pytest.mark.django_db
def test_wish_item_revtrieve__friend_status(user):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other')
    UserFriendshipFactory(sender=user, receiver=other_user, state=UserFriendshipState.ACCEPTED)
    wish_list = WishListFactory(owner=other_user)
    wish_item = WishItemFactory(name='item-1', list=wish_list)
    
    WishItemService.mark_to_gift(wish_item, user, True)
    response = client.get(f'/api/wishes/wish-item/{wish_item.id}/')
    assert response.data.get('state') == WishItemStatus.BOOKED_TO_GIFT
    assert response.data.get('to_be_gifted_by_id') == user.id

    client.force_authenticate(user=other_user)
    response = client.get(f'/api/wishes/wish-item/{wish_item.id}/')
    assert response.data.get('state') == WishItemStatus.OPEN
    assert response.data.get('to_be_gifted_by_id') == None

@pytest.mark.django_db
def test_wish_item_mark_to_gift__ok(user):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other')
    UserFriendshipFactory(sender=user, receiver=other_user, state=UserFriendshipState.ACCEPTED)

    wish_list = WishListFactory(owner=other_user)
    wish_item = WishItemFactory(name='item-1', list=wish_list)
    response = client.post(f'/api/wishes/wish-item/{wish_item.id}/mark-to-gift/', {'show_gifter_name': False}, format='json')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_wish_item_mark_to_gift__not_friend(user):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other')

    wish_list = WishListFactory(owner=other_user)
    wish_item = WishItemFactory(name='item-1', list=wish_list)
    response = client.post(f'/api/wishes/wish-item/{wish_item.id}/mark-to-gift/', {'show_gifter_name': False}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize('state', [WishItemStatus.BOOKED_TO_GIFT, WishItemStatus.GIFTED])
def test_wish_item_mark_to_gift__wrong_state(user, state):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other')
    UserFriendshipFactory(sender=user, receiver=other_user, state=UserFriendshipState.ACCEPTED)

    wish_list = WishListFactory(owner=other_user)
    wish_item = WishItemFactory(name='item-1', list=wish_list, state=state)
    response = client.post(f'/api/wishes/wish-item/{wish_item.id}/mark-to-gift/', {'show_gifter_name': False}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_wish_item__list(user):
    client = APIClient()
    client.force_authenticate(user=user)

    other_user = UserFactory(username='other-1')
    wish_list = WishListFactory(owner=other_user)
    wish_item = WishItemFactory(name='item-1', list=wish_list)
    UserFriendshipFactory(sender=user, receiver=other_user, state=UserFriendshipState.ACCEPTED)
    WishItemService.mark_to_gift(wish_item, user, True)

    other_user = UserFactory(username='other-2')
    wish_list = WishListFactory(owner=other_user)
    wish_item = WishItemFactory(name='item-1', list=wish_list)
    UserFriendshipFactory(sender=user, receiver=other_user, state=UserFriendshipState.ACCEPTED)
    WishItemService.mark_to_gift(wish_item, user, False)
    
    response = client.get('/api/wishes/wish-item/')
    wish_item.refresh_from_db()
    assert len(response.data) == 2

@pytest.mark.django_db
def test_wish_item__update(user):
    client = APIClient()
    client.force_authenticate(user=user)

    wish_list = WishListFactory(owner=user)
    wish_item = WishItemFactory(name='item-1', list=wish_list, comment='no comment')

    response = client.put(f'/api/wishes/wish-item/{wish_item.id}/', data={
        'name': 'item-2', 
        'comment': 'new comment', 
        'show_gifter_name': False}, 
        format='json')
    assert response.data['name'] == 'item-2'
    assert response.data['comment'] == 'new comment'
    wish_item.refresh_from_db()
    assert wish_item.name == 'item-2'
    assert wish_item.show_gifter_name