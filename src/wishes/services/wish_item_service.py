import datetime
from typing import Optional

from wishes.models import WishItem, WishList


class WishItemService:
    @classmethod
    def create_wish_item(
        cls, wish_list: WishList, name: str, comment: Optional[str], due_date: Optional[datetime.date]
    ) -> WishItem:
        return WishItem.objects.create(
            list=wish_list,
            name=name,
            comment=comment,
            due_date=due_date,
        )
