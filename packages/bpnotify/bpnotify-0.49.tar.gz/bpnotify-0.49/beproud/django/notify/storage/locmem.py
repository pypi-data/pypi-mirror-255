#:coding=utf-8:

from beproud.django.notify.storage.base import BaseStorage


class LocalMemoryStorage(BaseStorage):
    def __init__(self):
        self._data = {}

    def _get(self, key, default):
        return self._data.get(key, default)

    def _set(self, key, value):
        self._data[key] = value
        return True
