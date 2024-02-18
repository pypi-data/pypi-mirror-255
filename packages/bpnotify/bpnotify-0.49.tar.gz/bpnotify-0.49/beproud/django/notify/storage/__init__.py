#:coding=utf-8:

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from beproud.django.notify.constants import DEFAULT_SETTINGS_STORAGE
from beproud.django.notify.api import import_string

__all__ = (
    'get_storage',
    'storage',
)

def get_storage(storage_path, *args, **kwargs):
    try:
        return import_string(storage_path)(**kwargs)
    except (ImportError, AttributeError, ValueError) as e:
        raise ImproperlyConfigured('Error loading notify setting storage backend %s: "%s"' % (storage_path, e))

def load_storage(storage_setting):
    if isinstance(storage_setting, (list, tuple)):
        storage_path, kwargs = storage_setting
    else:
        storage_path, kwargs = storage_setting, {}
    return get_storage(storage_path, **kwargs)

storage = load_storage(getattr(settings, 'BPAUTH_SETTINGS_STORAGE', DEFAULT_SETTINGS_STORAGE))
