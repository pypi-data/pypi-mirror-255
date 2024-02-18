#:coding=utf8:
import six

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _
from django.db import models

from beproud.django.notify.api import _get_media_map

__all__ = (
    'Notification',
    'NotifySetting',
)


class MediaChoices(object):
    def __iter__(self):
        media_map = _get_media_map()
        return iter((name, data['verbose_name']) for name, data in six.iteritems(media_map))


class NotificationManager(models.Manager):
    def get_for_target(self, target):
        return self.filter(
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
        )


@six.python_2_unicode_compatible
class Notification(models.Model):
    target_content_type = models.ForeignKey(ContentType, verbose_name=_('content type id'),
                                            db_index=True, null=True, blank=True,
                                            on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField(_('target id'),
                                                   db_index=True, null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    notify_type = models.CharField(_('notify type'), max_length=100, db_index=True)
    media = models.CharField(_('media'), max_length=100, choices=MediaChoices(), db_index=True)

    extra_data = models.JSONField(_('extra data'), null=True, blank=True)

    ctime = models.DateTimeField(_('created'), auto_now_add=True, db_index=True)

    objects = NotificationManager()

    def __str__(self):
        return u"%s (%s, %s)" % (self.target, self.notify_type, self.media)

    class Meta:
        ordering = ('-ctime',)


@six.python_2_unicode_compatible
class NotifySetting(models.Model):
    target_content_type = models.ForeignKey(ContentType, verbose_name=_('content type id'), on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField(_('target id'))
    target = GenericForeignKey('target_content_type', 'target_object_id')

    notify_type = models.CharField(_('notify type'), max_length=100, db_index=True)
    media = models.CharField(_('media'), max_length=100, choices=MediaChoices(), db_index=True)
    send = models.BooleanField(_('send?'), default=False)

    def __str__(self):
        return u"%s (%s, %s, %s)" % (self.target, self.notify_type, self.media,
                                     self.send and 'send' or 'no send')

    class Meta:
        unique_together = ('target_content_type', 'target_object_id', 'notify_type', 'media')
