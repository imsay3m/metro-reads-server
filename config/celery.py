import logging
import os

from celery import Celery
from celery.signals import task_failure

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# Basic task failure monitoring: logs exceptions; extend to notify/email if needed
logger = logging.getLogger(__name__)


@task_failure.connect
def on_task_failure(sender=None, exception=None, traceback=None, einfo=None, **kwargs):
    task_name = getattr(sender, "name", str(sender))
    logger.error(
        "Celery task failed: %s | exception=%s",
        task_name,
        exception,
        exc_info=einfo and einfo.exception,
    )
