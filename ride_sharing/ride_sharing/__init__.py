from __future__ import absolute_import, unicode_literals

# This allows Celery to recognize your app.
# from .celery_app import app as celery_app
from celery_app import app

__all__ = ("app",)
