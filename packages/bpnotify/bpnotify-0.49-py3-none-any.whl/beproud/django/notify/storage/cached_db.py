#:coding=utf-8:

from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str
from django.core.cache import cache

from beproud.django.notify.storage.db import DBStorage

__all__ = ('CachedDBStorage',)


class CachedDBStorage(DBStorage):
    """
    A notification settings backend for storing user
    settings in the database. The settings are also
    cached using Django's cache framework.
    """

    def make_key(self, target, notify_type, media_name):
        content_type = ContentType.objects.get_for_model(target)
        key_list = (
            smart_str(target.pk),
            smart_str(content_type.pk),
            smart_str(notify_type),
            smart_str(media_name),
        )
        return u'bpnotify|setting|%s' % (':'.join(key_list))

    def get(self, target, notify_type, media_name, default=None):
        cache_key = self.make_key(target, notify_type, media_name)
        data = cache.get(cache_key, None)
        if data is None:
            data = super(CachedDBStorage, self).get(
                target,
                notify_type,
                media_name,
                None
            )
            if data is not None:
                cache.set(cache_key, data)
            else:
                data = default
        return data

    def set(self, target, notify_type, media_name, send):
        saved = super(CachedDBStorage, self).set(
            target,
            notify_type,
            media_name,
            send,
        )
        if saved:
            cache.set(self.make_key(target, notify_type, media_name), send)
        return saved
