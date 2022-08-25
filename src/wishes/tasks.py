from datetime import datetime
from celeryapp.app import app
from wishes.models import WishItem
from wishes.constants import WishItemStatus

@app.task
def mark_outdated_items() -> None:
    WishItem.objects.all().update(state=WishItemStatus.OUTDATED)