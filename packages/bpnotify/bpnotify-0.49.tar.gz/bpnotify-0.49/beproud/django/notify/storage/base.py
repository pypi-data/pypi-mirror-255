#:coding=utf-8:

from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str


class BaseStorage(object):
    """
    This is the base backend for user identification data storage.

    This is not a complete class; to be a usable storage backend, it must be
    subclassed and the two methods ``_get`` and ``_set`` overridden.
    """

    def __init__(self, *args, **kwargs):
        super(BaseStorage, self).__init__(*args, **kwargs)

    def make_key(self, target, notify_type, media_name):
        content_type = ContentType.objects.get_for_model(target)
        key_list = (
            smart_str(target.pk),
            smart_str(content_type.pk),
            smart_str(notify_type),
            smart_str(media_name),
        )
        return u'bpnotify|%s' % (':'.join(key_list))

    def get(self, target, notify_type, media_name, default=None):
        """
        Get the setting for the given notify_type, and media for the
        given user.
        """
        return self._get(self.make_key(target, notify_type, media_name), default)

    def _get(self, key, default=None):
        raise NotImplementedError

    def set(self, target, notify_type, media_name, send):
        """
        Set the setting for the given notify_type, and media for the
        given user.
        """
        return self._set(self.make_key(target, notify_type, media_name), send)

    def _set(self, key, send):
        raise NotImplementedError
