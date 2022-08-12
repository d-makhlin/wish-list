from django.contrib import admin

from user.models import UserFriendship


@admin.register(UserFriendship)
class UserFriendshipAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'sender',
        'receiver',
        'state',
        'create_date',
        'modify_date'
    )
    list_filter = ('sender', 'receiver')
    search_fields = ('sender__id', 'receiver__id')
    ordering = ('-create_date',)
