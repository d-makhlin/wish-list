"""wishList URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user import views as user_view
from wishes import views as wishes_view
from django.contrib.auth import views as auth
from rest_framework_simplejwt import views as jwt_views


router = DefaultRouter(trailing_slash=True)
router.register('wishes/wish-list', wishes_view.WishListView, 'wishes-wish-list')
router.register('wishes/wish-item', wishes_view.WishItemView, 'wishes-wish-item')
router.register('user/friendship', user_view.UserFriendshipView, 'user-friendship')
router.register('user/users', user_view.UserView, 'user-users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('', include('user.urls')),
    path('login/', user_view.Login, name='login'),
    path('logout/', auth.LogoutView.as_view(template_name='user/index.html'), name='logout'),
    path('register/', user_view.register, name='register'),
]
