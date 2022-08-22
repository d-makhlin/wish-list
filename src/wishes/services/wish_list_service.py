from user.models import User
from wishes.models import WishList


class WishListService:
    @staticmethod
    def create_wish_list(user: User, name: str) -> WishList:
        return WishList.objects.create(
            name=name,
            owner=user,
        )
