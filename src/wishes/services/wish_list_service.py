from user.models import User
from wishes.models import WishList


class WishListService:
    @classmethod
    def create_wish_list(
            cls, user: User, name: str
    ) -> WishList:
        return WishList.objects.create(
            name=name,
            owner=user,
        )
