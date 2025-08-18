"""
Celery config file
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html
"""

from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
app = Celery("api")

# Using a string here means the worker will not have to
# pickle the object when using Windows.

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    # Add some schedule tasks here if you need
    # Example:
    # 'send_welcome_email': {
    #     'task': 'api.tasks.send_account_activation_post_email,
    #     'schedule': crontab(minute=0, hour=7)
    # },
}

app.autodiscover_tasks()
