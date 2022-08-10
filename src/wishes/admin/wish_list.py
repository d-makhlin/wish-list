from django.contrib import admin

from wishes.models import WishList


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'name',
        'owner',
        'create_date',
    )
    search_fields = ('owner__id',)
    ordering = ('-create_date',)
