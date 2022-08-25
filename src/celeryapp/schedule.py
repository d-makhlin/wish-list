"""
Celery beat config is applied on celery-beat start automatically
"""
from datetime import timedelta
from typing import Any, Dict

def get_beat_schedule() -> Dict[str, Any]:
    beat_schedule = dict(BEAT_SCHEDULE)
    return beat_schedule


BEAT_SCHEDULE = {
    'mark_outdated_items': {
        'task': 'wishes.tasks.mark_outdated_items',
        'schedule': timedelta(seconds=30),  # every day after start celery beat
    },
}