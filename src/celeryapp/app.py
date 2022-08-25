import os

from celery import Celery

from .schedule import get_beat_schedule

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

app = Celery('wish-list')
app.config_from_object('conf.settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.beat_schedule = get_beat_schedule()
