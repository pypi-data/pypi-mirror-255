#:coding=utf-8:

from django.conf import settings

__all__ = ('TestBase',)

AVAILABLE_SETTINGS = (
    'MIDDLEWARE_CLASSES',
    'BPNOTIFY_MEDIA',
    'BPNOTIFY_SETTINGS_BACKEND',
)

class TestBase(object):
    def setUp(self):
        for setting_name in AVAILABLE_SETTINGS:
            setting_value = getattr(self, setting_name, None)
            setattr(self, "_old_"+setting_name, getattr(settings, setting_name, None))
            if setting_value:
                setattr(settings, setting_name, setting_value)

    def tearDown(self):
        for setting_name in AVAILABLE_SETTINGS:
            old_setting_value = getattr(self, "_old_"+setting_name, None)
            if old_setting_value is None:
                if hasattr(settings, setting_name):
                    delattr(settings, setting_name)
            else:
                setattr(settings, setting_name, old_setting_value)
