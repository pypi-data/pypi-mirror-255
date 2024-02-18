#:coding=utf8:

import logging

import six

from django.core.exceptions import ImproperlyConfigured

if six.PY2:
    from django.utils.encoding import force_unicode

__all__ = (
    'load_backend',
    'notify',
    'notify_now',
    'get_notifications',
    'get_notification_count',
    'get_notify_setting',
    'set_notify_setting',
    'NotifyObjectList',
)

logger = logging.getLogger('beproud.django.notify')


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    if isinstance(import_name, six.text_type):
        import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        if six.PY2 and isinstance(obj, six.text_type):
            obj = obj.encode('utf-8')
        return getattr(__import__(module, None, None, [obj]), obj)
    except (ImportError, AttributeError):
        if not silent:
            raise


def _capfirst(value):
    if value:
        if six.PY2:
            value = force_unicode(value)
        return "%s%s" % (value[0].upper(), value[1:])
    else:
        return value


def _get_media_map():
    from django.conf import settings

    media_settings = getattr(settings, 'BPNOTIFY_MEDIA', {})
    media_map = {}
    for name in media_settings:
        media_map[name] = _get_media_settings(name)
    return media_map


def _get_media_settings(media):
    from django.conf import settings

    media_settings = getattr(settings, 'BPNOTIFY_MEDIA', {}).get(media, {})
    return {
        'verbose_name': media_settings.get('verbose_name', _capfirst(media)),
        'default_types': media_settings.get('default_types', ()),
        'backends': [load_backend(path) for path in media_settings.get('backends', ())],
    }


def load_backend(backend_path):
    """
    Load the auth backend with the given name
    """
    kwargs = {}
    if isinstance(backend_path, (list, tuple)):
        backend_path, kwargs = backend_path

    try:
        return import_string(backend_path)(**kwargs)
    except (ImportError, AttributeError) as e:
        raise ImproperlyConfigured('Error importing notify backend %s: "%s"' % (backend_path, e))
    except ValueError as e:
        raise ImproperlyConfigured("Error importing notify backends. "
                                   "Is BPNOTIFY_MEDIA a correctly defined dict?")


def notify(targets, notify_type, extra_data={}, include_media=None, exclude_media=[]):
    from django.conf import settings

    if 'djcelery' in settings.INSTALLED_APPS:
        from beproud.django.notify import tasks

        if not hasattr(targets, '__iter__'):
            targets = [targets]

        tasks.Notify.delay(
            targets=targets,
            notify_type=notify_type,
            extra_data=extra_data,
            include_media=include_media,
            exclude_media=exclude_media,
        )
        return len(targets)
    else:
        return notify_now(targets, notify_type, extra_data, include_media, exclude_media)


def notify_now(targets, notify_type, extra_data={}, include_media=None, exclude_media=[]):
    u"""
    Send a notification to the appropriate media based on the notify type.

    include_media: A list of media names to include.

    """
    if not hasattr(targets, '__iter__'):
        targets = [targets]

    media_map = _get_media_map()
    if include_media:
        include_media = [media for media in include_media if media in media_map]
    else:
        include_media = [media for media in media_map if media not in exclude_media]

    num_sent = 0
    for media_name in include_media:
        media_settings = media_map[media_name]

        targets_to_send = list(filter(lambda t: get_notify_setting(t, notify_type, media_name), targets))
        if targets_to_send:
            for backend in media_settings['backends']:
                num_sent += backend.send(targets_to_send, notify_type, media_name, extra_data)
    return num_sent

# The maximum number of items to display in a NotifyObjectList.__repr__
REPR_OUTPUT_SIZE = 20


class NotifyObjectList(object):
    """
    An object list that retrieves notifications.
    Allows for paginating notifications.
    """
    def __init__(self, target, media):
        self.target = target
        self.media = media

    def __getitem__(self, key):
        if not isinstance(key, (slice, six.integer_types)):
            raise TypeError
        if isinstance(key, slice):
            notices = get_notifications(
                target=self.target,
                media_name=self.media,
                start=key.start,
                end=key.stop,
            )
            return key.step and list()[::key.step] or notices
        else:
            notices = get_notifications(
                target=self.target,
                media_name=self.media,
                start=key,
                end=key,
            )
            if notices:
                return notices
            else:
                raise IndexError("list index out of range")

    def __iter__(self):
        return self.iterator()

    def iterator(self):
        index = 0
        try:
            notice = get_notifications(
                target=self.target,
                media_name=self.media,
                start=index,
                end=index+1,
            )
            while notice:
                yield notice[0]
                index += 1
                notice = get_notifications(
                    target=self.target,
                    media_name=self.media,
                    start=index,
                    end=index+1,
                )
        except KeyError:
            pass

    def __len__(self):
        return get_notification_count(
            target=self.target,
            media_name=self.media,
        )

    def __repr__(self):
        data = list(self[:REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return repr(data)


def get_notifications(target, media_name, start=None, end=None):
    """
    Retrieves notifications for the given media from the first
    backend that supports retrieving. Backends that raise a
    NotImplementedError will be ignored.

    The list of notifications will be an iterable of dicts
    in the following format:

    {
        'id': unique_id,
        'target': target,
        'notify_type': notify_type,
        'media': media,
        'extra_data': {
            'spam': 'eggs',
        }
        'ctime': datetime.datetime(...),
    }
    """
    media_map = _get_media_map()
    media_settings = media_map.get(media_name)
    if media_settings:
        for backend in media_settings['backends']:
            try:
                return backend.get(target, media_name, start, end)
            except NotImplementedError:
                logger.debug('''Backend "%s" doesn't support retrieval. skipping.''' % backend)
    return []


def get_notification_count(target, media_name):
    """
    Retrieves the number of notifications for the given media from the first
    backend that supports retrieving counts. Backends that raise a
    NotImplemented exception will be ignored.

    If no backend supports retrieving counts then 0 is returned.
    """
    media_map = _get_media_map()
    media_settings = media_map.get(media_name)
    if media_settings:
        for backend in media_settings['backends']:
            try:
                return backend.count(target, media_name)
            except NotImplementedError:
                logger.debug('''Backend "%s" doesn't support counts. skipping.''' % backend)
    return 0


def get_notify_setting(target, notify_type, media_name, default=None):
    """
    Gets whether to send notifications with the given notify type
    to the given media. A default value can be provided.

    If no default value is provided, the default is True if the
    notify type is in the default_types setting for the given media.

    If neither the notify_type or the media are recognized, then this
    function will return False and no notifications are sent.
    """
    from beproud.django.notify.storage import storage

    media_settings = _get_media_settings(media_name)

    if default is None:
        default = notify_type in media_settings.get('default_types', [])

    # Special case for the null target
    if target is None:
        return default

    return storage.get(target, notify_type, media_name, default)


def set_notify_setting(target, notify_type, media_name, send):
    """
    Sets whether to send notifications with the given notify type
    to the given media. The default storage backend is used
    to store the settings.
    """

    # Special case for the null target
    if target is None:
        return False

    from beproud.django.notify.storage import storage
    return storage.set(target, notify_type, media_name, send)
