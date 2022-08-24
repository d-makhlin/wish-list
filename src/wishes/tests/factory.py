from common.base import BaseFactory
from wishes.models import WishItem, WishList


class WishItemFactory(BaseFactory):
    class Meta:
        model = WishItem


class WishListFactory(BaseFactory):
    class Meta:
        model = WishList
