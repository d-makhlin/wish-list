import datetime
from typing import Optional

from django.db.models import QuerySet

from user.models import User
from user.services.user_friendship_service import UserFriendshipService
from wishes.constants import WishItemStatus
from wishes.models import WishItem, WishList


class WishItemService:
    @staticmethod
    def create_wish_item(
        wish_list: WishList, name: str, comment: Optional[str], due_date: Optional[datetime.date]
    ) -> WishItem:
        if due_date:
            # call celery task
            pass
        item = WishItem.objects.create(
            list=wish_list,
            name=name,
            comment=comment,
            due_date=due_date,
        )
        return item

    @staticmethod
    def mark_to_gift(wish_item: WishItem, user: User, show_name: bool) -> bool:
        if wish_item.state != WishItemStatus.OPEN:
            return False  # item is unavailable

        if not UserFriendshipService.is_in_friendship(wish_item.list.owner_id, user.id):
            return False  # user is not a friend of the item owner

        wish_item.to_be_gifted_by = user
        wish_item.show_gifter_name = show_name
        wish_item.state = WishItemStatus.BOOKED_TO_GIFT
        wish_item.save()
        UserFriendshipService.notify_friends(wish_item.list.owner_id)
        return True

    @staticmethod
    def get_items_to_gift(user_id: str) -> QuerySet[WishItem]:
        return WishItem.objects.filter(
            to_be_gifted_by_id=user_id, state__in=(WishItemStatus.BOOKED_TO_GIFT, WishItemStatus.GIFTED)
        )
