__version__ = "0.0.1"
"""
This webhook app was forked from https://github.com/danihodovic/django-webhook
and modified to work with kitchenai.

Main changes:
- Removed all the code that was not needed for kitchenai.
- Added support for django-q2 via async tasks instead of celery.
"""
