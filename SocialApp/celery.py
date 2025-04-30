# myproject/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SocialApp.settings')

app = Celery('SocialApp')

# Use a string here to avoid pickle issues with Windows
# Configure Celery using settings from Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
