from django.contrib import admin

from wishes.models import WishItem


@admin.register(WishItem)
class WishItemAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'name',
        'list',
        'due_date',
        'state',
        'comment',
        'to_be_gifted_by',
        'create_date',
    )
    raw_id_fields = ('list',)
    list_filter = ('list', 'to_be_gifted_by')
    search_fields = ('to_be_gifted_by__id',)
    ordering = ('-create_date',)
