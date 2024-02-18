#:coding=utf-8:

from django.contrib.contenttypes.models import ContentType
from django.db import DatabaseError

from beproud.django.notify.backends.base import BaseBackend


class ModelBackend(BaseBackend):
    """
    A basic backend that saves to the default
    Notification model. Targets must be Django model objects or None.
    Extra data must be JSON serializable.
    """
    def _send(self, target, notify_type, media, extra_data={}):
        from beproud.django.notify.models import Notification

        notification = Notification(
            notify_type=notify_type,
            media=media,
            extra_data=extra_data,
        )
        notification.target = target

        try:
            notification.save()
            return 1
        except (TypeError, DatabaseError):
            # extra_data could not be serialized to JSON or
            # there was some kind of Database error
            # TODO: logging
            return 0

    def get(self, target, media, start=None, end=None):
        from beproud.django.notify.models import Notification

        filter_kwargs = {
            'media': media,
        }
        if target is None:
            filter_kwargs['target_content_type__isnull'] = True
            filter_kwargs['target_object_id__isnull'] = True
        else:
            filter_kwargs['target_content_type'] = ContentType.objects.get_for_model(target)
            filter_kwargs['target_object_id'] = target.pk

        notifications = Notification.objects.filter(**filter_kwargs).order_by('-ctime')

        if start is not None or end is not None:
            if start is None:
                notifications = notifications[:end]
            elif end is None:
                notifications = notifications[start:]
            else:
                notifications = notifications[start:end]

        return [{
            'id': 'Notification:%s' % n.id,
            'target': n.target,
            'notify_type': n.notify_type,
            'media': n.media,
            'extra_data': n.extra_data,
            'ctime': n.ctime,
        } for n in notifications]

    def count(self, target, media):
        from beproud.django.notify.models import Notification
        return Notification.objects.filter(
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            media=media,
        ).count()
