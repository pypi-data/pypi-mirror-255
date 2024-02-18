#:coding=utf8:

from unittest import mock

from django.test import TestCase
from django.contrib.auth.models import User

from beproud.django.notify.tests.utils import override_settings
from beproud.django.notify.models import Notification
from beproud.django.notify import tasks as notify_tasks
from beproud.django.notify import api as notify_api

__all__ = (
    'TaskTests',
)

class TaskTests(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        # Clear the media settings
        notify_api._media_map_cache = {}

    @override_settings(
        BPNOTIFY_MEDIA = {
            "news": {
                "verbose_name": "News",
                "default_types": ("private_msg",),
                "backends": (
                    "beproud.django.notify.backends.model.ModelBackend",
                ),
            },
        },
        # Celery only looks at this setting once on startup so
        # it can't be overridden.
        # CELERY_ALWAYS_EAGER=True,
    )
    def test_notify_task(self): 
        """
        Simple task to test the Notify task.
        """
        user = User.objects.get(pk=2)
        notify_tasks.notify.delay(
            targets=[user],
            notify_type='private_msg',
        )

        private_messages = Notification.objects.filter(media="news")
        self.assertEqual(len(private_messages), 1)
        self.assertEqual(private_messages[0].notify_type, 'private_msg')
        self.assertEqual(private_messages[0].target, user)

    @mock.patch.object(notify_tasks, 'notify_now')
    def test_notify_task_retry(self, notify_now):
        def _notify_now(*args, **kwargs):
            if not hasattr(_notify_now, 'call_count'):
                _notify_now.call_count = 1
            else:
                _notify_now.call_count += 1

            # Error happens 3 times but we retry all
            # three times.
            if _notify_now.call_count < 3:
                raise RuntimeError("Some Error")

            return 1
        notify_now.side_effect = _notify_now

        user = User.objects.get(pk=2)
        notify_tasks.notify.delay(
            targets=[user],
            notify_type='private_msg',
        )

        # First call + 2 retries = 3 calls
        self.assertEqual(notify_now.call_count, 3)

    @mock.patch.object(notify_tasks, 'notify_now')
    def test_notify_task_retry_fail(self, notify_now):
        def _notify_now(*args, **kwargs):
            if not hasattr(_notify_now, 'call_count'):
                _notify_now.call_count = 1
            else:
                _notify_now.call_count += 1

            # Error happens 5 times but we only
            # retry 3 times.
            if _notify_now.call_count < 5:
                raise RuntimeError("Some Error")

            return 1
        notify_now.side_effect = _notify_now

        user = User.objects.get(pk=2)
        notify_tasks.notify.delay(
            targets=[user],
            notify_type='private_msg',
        )

        # First call + 3 retries = 4 calls
        self.assertEqual(notify_now.call_count, 4)
