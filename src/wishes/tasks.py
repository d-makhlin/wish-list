from datetime import datetime
from celeryapp.app import app
from wishes.models import WishItem
from wishes.constants import WishItemStatus

@app.task
def mark_outdated_items() -> None:
    WishItem.objects.filter(
        due_date__lt=datetime.today(), 
        state__in=(WishItemStatus.OPEN, WishItemStatus.BOOKED_TO_GIFT)
        ).update(state=WishItemStatus.OUTDATED)