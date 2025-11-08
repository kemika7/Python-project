"""
Celery configuration for JobMarketTracker
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobMarketTracker.settings')

app = Celery('JobMarketTracker')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule
app.conf.beat_schedule = {
    'run-job-spider-every-6-hours': {
        'task': 'jobdata.tasks.run_job_spider',
        'schedule': 21600.0,  # 6 hours in seconds
    },
    'analyze-skills-hourly': {
        'task': 'jobdata.tasks.analyze_skills_task',
        'schedule': 3600.0,  # 1 hour in seconds
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

