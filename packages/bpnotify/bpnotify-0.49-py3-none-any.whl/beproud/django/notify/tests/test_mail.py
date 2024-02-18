#:coding=utf8:

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from beproud.django.notify.tests.base import TestBase

from beproud.django.notify.api import notify_now

__all__ = ('MailNotifyTest',)

class MailNotifyTest(TestBase, TestCase):
    fixtures = ['test_users.json']
    
    def test_sending_mail(self):
        user = User.objects.get(pk=2)
        items_sent = notify_now(user, 'private_msg', extra_data={"spam": "eggs"})

        # 1 private_messages model
        # 1 news model
        # 1 private_messages mail
        self.assertEqual(items_sent, 3)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, u'テストメール private_msg private_messages eggs')
        self.assertEqual(mail.outbox[0].body, u'Text メールボディ private_msg private_messages eggs\n')

    def test_from_email(self):
        user = User.objects.get(pk=2)
        notify_now(user, 'private_msg', extra_data={"spam": "eggs", "from_email": "spameggs@example.com"})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, "spameggs@example.com")

    def test_from_mail(self):
        user = User.objects.get(pk=2)
        notify_now(user, 'private_msg', extra_data={"spam": "eggs", "from_mail": "spameggs@example.com"})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, "spameggs@example.com")
