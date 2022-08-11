from django.urls import path

from .views import WishItemView
from .views import WishListView

urlpatterns = [
    path('wish-list/', WishListView, name='wish-list'),
    path('wish-item/', WishItemView, name='wish-item'),
]
