#:coding=utf8:

from django.contrib import admin

from beproud.django.notify.models import Notification, NotifySetting 

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('target_content_type','target_object_id', 'notify_type','media')
    list_filter = ('target_content_type', 'notify_type', 'media')
    ordering = ('-ctime',)

class NotifySettingAdmin(admin.ModelAdmin):
    list_display = ('target','notify_type','media','send')
    list_filter = ('target_content_type','notify_type', 'media')
    ordering = ('target_content_type','target_object_id')

admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotifySetting, NotifySettingAdmin)
