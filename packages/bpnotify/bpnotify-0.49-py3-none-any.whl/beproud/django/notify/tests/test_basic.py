#:coding=utf8:

from datetime import datetime
import six

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.test import TestCase

from beproud.django.notify.tests.base import TestBase
from beproud.django.notify.models import Notification, NotifySetting
from beproud.django.notify.api import (
    notify_now,
    set_notify_setting,
    get_notify_setting,
    get_notifications,
    NotifyObjectList,
)

__all__ = (
    'BasicNotifyTest',
    'ModelUnicodeTest',
)

class BasicNotifyTest(TestBase, TestCase):
    fixtures = ['test_users.json']
    
    def test_sending_model(self):
        user = User.objects.get(pk=2)
        items_sent = notify_now(user, 'follow', extra_data={"followed": "eggs"})
        # 1 news model
        self.assertEqual(items_sent, 1)

        news = Notification.objects.filter(media='news')
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0].media, 'news')
        self.assertEqual(news[0].notify_type, 'follow')
        self.assertEqual(news[0].target, user)
        self.assertEqual(news[0].extra_data.get('followed'), 'eggs')
        
        private_messages = Notification.objects.exclude(media='news')
        self.assertEqual(len(private_messages), 0)

    def test_sending_model_null(self):
        items_sent = notify_now(None, 'follow', extra_data={"followed": "eggs"})
        # 1 news model
        self.assertEqual(items_sent, 1)

        news = Notification.objects.filter(media='news')
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0].media, 'news')
        self.assertEqual(news[0].notify_type, 'follow')
        self.assertEqual(news[0].target, None)
        self.assertEqual(news[0].extra_data.get('followed'), 'eggs')
        
        private_messages = Notification.objects.exclude(media='news')
        self.assertEqual(len(private_messages), 0)

    def test_sending_model_types(self):
        user = User.objects.get(pk=2)
        items_sent = notify_now(user, 'private_msg', extra_data={"spam": "eggs"})
        # 1 private_messages model
        # 1 private_messages mail
        # 1 news model
        self.assertEqual(items_sent, 3)

        private_messages = Notification.objects.filter(media='private_messages')
        self.assertEqual(len(private_messages), 1)
        self.assertEqual(private_messages[0].media, 'private_messages')
        self.assertEqual(private_messages[0].notify_type, 'private_msg')
        self.assertEqual(private_messages[0].target, user)
        self.assertEqual(private_messages[0].extra_data.get('spam'), 'eggs')

        news = Notification.objects.filter(media='news')
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0].media, 'news')
        self.assertEqual(news[0].notify_type, 'private_msg')
        self.assertEqual(news[0].target, user)
        self.assertEqual(news[0].extra_data.get('spam'), 'eggs')

    def test_sending_model_types_null(self):
        items_sent = notify_now(None, 'private_msg', extra_data={"spam": "eggs"})
        # 1 private_messages model
        # 0 private_messages mail (No mail to null target)
        # 1 news model
        self.assertEqual(items_sent, 2)

        private_messages = Notification.objects.filter(media='private_messages')
        self.assertEqual(len(private_messages), 1)
        self.assertEqual(private_messages[0].media, 'private_messages')
        self.assertEqual(private_messages[0].notify_type, 'private_msg')
        self.assertEqual(private_messages[0].target, None)
        self.assertEqual(private_messages[0].extra_data.get('spam'), 'eggs')

        news = Notification.objects.filter(media='news')
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0].media, 'news')
        self.assertEqual(news[0].notify_type, 'private_msg')
        self.assertEqual(news[0].target, None)
        self.assertEqual(news[0].extra_data.get('spam'), 'eggs')


    def test_sending_model_multi(self):
        user = [User.objects.get(pk=1), User.objects.get(pk=2), None]
        items_sent = notify_now(user, 'private_msg', extra_data={"spam": "eggs"})

        # 3 private_messages model
        # 2 private_messages mail (No mail to null target)
        # 3 news model
        self.assertEqual(items_sent, 8)

        # User1
        private_messages = Notification.objects.filter(
            media='private_messages',
            target_content_type=ContentType.objects.get_for_model(user[0]),
            target_object_id=user[0].id,
        )
        self.assertEqual(len(private_messages), 1)
        self.assertEqual(private_messages[0].media, 'private_messages')
        self.assertEqual(private_messages[0].notify_type, 'private_msg')
        self.assertEqual(private_messages[0].target, user[0])
        self.assertEqual(private_messages[0].extra_data.get('spam'), 'eggs')

        news = Notification.objects.filter(
            media='news',
            target_content_type=ContentType.objects.get_for_model(user[0]),
            target_object_id=user[0].id,
        )
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0].media, 'news')
        self.assertEqual(news[0].notify_type, 'private_msg')
        self.assertEqual(news[0].target, user[0])
        self.assertEqual(news[0].extra_data.get('spam'), 'eggs')

        # User2
        private_messages = Notification.objects.filter(
            media='private_messages',
            target_content_type=ContentType.objects.get_for_model(user[1]),
            target_object_id=user[1].id,
        )
        self.assertEqual(len(private_messages), 1)
        self.assertEqual(private_messages[0].media, 'private_messages')
        self.assertEqual(private_messages[0].notify_type, 'private_msg')
        self.assertEqual(private_messages[0].target, user[1])
        self.assertEqual(private_messages[0].extra_data.get('spam'), 'eggs')

        news = Notification.objects.filter(
            media='news',
            target_content_type=ContentType.objects.get_for_model(user[1]),
            target_object_id=user[1].id,
        )
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0].media, 'news')
        self.assertEqual(news[0].notify_type, 'private_msg')
        self.assertEqual(news[0].target, user[1])
        self.assertEqual(news[0].extra_data.get('spam'), 'eggs')

        # Null Target
        private_messages = Notification.objects.filter(
            media='private_messages',
            target_content_type__isnull=True,
            target_object_id__isnull=True,
        )
        self.assertEqual(len(private_messages), 1)
        self.assertEqual(private_messages[0].media, 'private_messages')
        self.assertEqual(private_messages[0].notify_type, 'private_msg')
        self.assertEqual(private_messages[0].target, None)
        self.assertEqual(private_messages[0].extra_data.get('spam'), 'eggs')

        news = Notification.objects.filter(
            media='news',
            target_content_type__isnull=True,
            target_object_id__isnull=True,
        )
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0].media, 'news')
        self.assertEqual(news[0].notify_type, 'private_msg')
        self.assertEqual(news[0].target, None)
        self.assertEqual(news[0].extra_data.get('spam'), 'eggs')

    def test_sending_with_settings(self):
        user = [User.objects.get(pk=1), User.objects.get(pk=2)]

        items_sent = notify_now(user, 'followed', extra_data={"spam": "eggs"})
        self.assertEqual(items_sent, 0)

        self.assertTrue(set_notify_setting(user[0], 'followed', 'news', True))
        items_sent = notify_now(user, 'followed', extra_data={"spam": "eggs"})

        # 1 news model
        self.assertEqual(items_sent, 1)

    def test_settings_null(self):
        self.assertFalse(set_notify_setting(None, 'followed', 'news', True))

        # get_notify_setting for null target always returns the default
        self.assertTrue(get_notify_setting(None, 'followed', 'news', True))
        self.assertFalse(get_notify_setting(None, 'followed', 'news'))
        self.assertFalse(get_notify_setting(None, 'follow', 'news', False))
        self.assertTrue(get_notify_setting(None, 'follow', 'news'))

    def test_get_notifications(self):
        user = [User.objects.get(pk=1), User.objects.get(pk=2)]
        items_sent = notify_now(user, 'private_msg', extra_data={"spam": "eggs"})

        # 2 private_messages model
        # 2 private_messages mail
        # 2 news model
        self.assertEqual(items_sent, 6)

        for index in [0, 1]:
            news = get_notifications(user[index], 'news')
            self.assertTrue(hasattr(news, '__iter__'), 'news notifications is not an iterable!')
            self.assertEqual(len(news), 1)
            self.assertTrue(isinstance(news[0], dict), 'news notification is not a dict!')
            self.assertTrue(news[0].get('id', False), 'news notification has no id')
            self.assertEqual(news[0].get('target'), user[index])
            self.assertEqual(news[0].get('notify_type'), 'private_msg')
            self.assertEqual(news[0].get('media'), 'news')
            self.assertEqual(news[0].get('extra_data'), {'spam': 'eggs'})
            self.assertTrue(isinstance(news[0].get('ctime'), datetime), 'news ctime is not a datetime!')


            private_messages = get_notifications(user[index], 'private_messages')
            self.assertTrue(hasattr(private_messages, '__iter__'), 'private_messages notifications is not an iterable!')
            self.assertEqual(len(private_messages), 1)
            self.assertTrue(isinstance(private_messages[0], dict), 'private_messages notification is not a dict!')
            self.assertTrue(private_messages[0].get('id', False), 'private_messages notification has no id')
            self.assertEqual(private_messages[0].get('target'), user[index])
            self.assertEqual(private_messages[0].get('notify_type'), 'private_msg')
            self.assertEqual(private_messages[0].get('media'), 'private_messages')
            self.assertEqual(private_messages[0].get('extra_data'), {'spam': 'eggs'})
            self.assertTrue(isinstance(news[0].get('ctime'), datetime), 'news ctime is not a datetime!')

    def test_object_list(self):
        user = User.objects.get(pk=2)
        for i in range(15):
            notify_now(user, 'follow', extra_data={"followed": "eggs"})
        
        object_list = NotifyObjectList(user, 'news')
        self.assertEqual(len(object_list), 15)
        
        count = 0
        for notice in object_list:
            count += 1
            self.assertTrue('id' in notice)
            self.assertEqual(notice['media'], 'news')
            self.assertEqual(notice['notify_type'], 'follow')
        self.assertEqual(count, 15)
        
        self.assertEqual(len(object_list[:5]), 5)
        self.assertEqual(len(object_list[1:]), 14)
        self.assertEqual(len(object_list[1:3]), 2)
        self.assertEqual(len(list(object_list)), 15)

    def test_object_list_failures(self):
        user = User.objects.get(pk=2)
        object_list = NotifyObjectList(user, 'news')
    
        self.assertEqual(len(object_list), 0)

        try:
            object_list[10]
            self.fail("Expected IndexError")
        except IndexError:
            pass

        self.assertEqual(object_list[10:11], [])
        self.assertEqual(object_list[:11], [])
        self.assertEqual(object_list[2:], [])

    def test_notify_type_length(self):
        # Test notify_types with length over 30
        user = User.objects.get(pk=2)
        items_sent = notify_now(user, 'notify_type_with_length_over_thirty')
        # 1 news model
        self.assertEqual(items_sent, 1)

        self.assertEqual(
            Notification.objects.filter(notify_type='notify_type_with_length_over_thirty').count(),
            1,
        )

class ModelUnicodeTest(TestCase):
    def test_notification_unicode(self):
        notice = Notification()
        self.assertEqual(str(notice), "None (, )")
        notice.notify_type = u"テスト"
        notice.media = "yyy"
        if six.PY2:
            self.assertEqual(str(notice), u"None (テスト, yyy)".encode("utf-8"))
        else:
            self.assertEqual(str(notice), "None (テスト, yyy)")

    def test_notification_setting_unicode(self):
        setting = NotifySetting()
        self.assertEqual(str(setting), "None (, , no send)")

        setting.notify_type = u"テスト"
        setting.media = "yyy"
        setting.send = True
        if six.PY2:
            self.assertEqual(str(setting), u"None (テスト, yyy, send)".encode("utf-8"))
        else:
            self.assertEqual(str(setting), "None (テスト, yyy, send)")
