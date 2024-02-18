#:coding=utf-8:

import logging

from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import get_connection, EmailMessage, EmailMultiAlternatives
from django.conf import settings

from beproud.django.notify.backends.base import BaseBackend

logger = logging.getLogger('beproud.django.notify')


class EmailBackend(BaseBackend):
    """
    A backend that sends email for the given notification type.

    The email content is rendered from a template found in the
    following templates:

    notify/<notify_type>/<media>/mail_subject.txt
    notify/<notify_type>/<media>/mail_body.html
    notify/<notify_type>/<media>/mail_body.txt

    The body templates can contain both html and text, only html, or only text.
    The EmailBackend does the following:

    The email recipient is retrieved from each target object by searching for a
    "email" or "mail" property. If none is found the extra_data dictionary is
    searched for a "email" or "mail" key.

    If no recipient email could be retrieved or a subject template could not
    be found then the mail is not sent.

    If only a text template is found then the email is sent as text.
    If only a html template is found then the email is send as multipart with a
    text body created by stripping html tags from the html body.
    If both html and a text template are found then the email is sent as multipart
    with the rendered content.
    """
    def send(self, targets, notify_type, media, extra_data={}):

        subject_template = 'notify/%s/%s/mail_subject.txt' % (notify_type, media)
        body_html_template = 'notify/%s/%s/mail_body.html' % (notify_type, media)
        body_text_template = 'notify/%s/%s/mail_body.txt' % (notify_type, media)

        messages = []
        if targets:
            try:
                for target in targets:
                    to_email = getattr(target, 'email',
                                       getattr(target, 'mail',
                                               extra_data.get('email', extra_data.get('mail'))))
                    from_email = extra_data.get('from_email',
                                                extra_data.get('from_mail',
                                                               settings.DEFAULT_FROM_EMAIL))

                    if to_email:
                            context = {
                                'target': target,
                                'notify_type': notify_type,
                                'media': media,
                            }
                            context.update(extra_data)

                            subject = render_to_string(subject_template, context)
                            subject = subject.replace(u"\r", u"").replace(u"\n", u"")

                            try:
                                body_html = render_to_string(body_html_template, context)
                            except TemplateDoesNotExist as e:
                                body_html = None

                            try:
                                body_text = render_to_string(body_text_template, context)
                            except TemplateDoesNotExist as e:
                                body_text = None

                            if body_html and not body_text:
                                body_text = strip_tags(body_html)

                            if body_text and body_html:
                                # HTML mail
                                message = EmailMultiAlternatives(subject, body_text, to=[to_email],
                                                                 from_email=from_email)
                                message.attach_alternative(body_html, "text/html")
                                messages.append(message)
                            elif body_text:
                                # Normal Text Mail
                                messages.append(EmailMessage(subject, body_text,
                                                             to=[to_email], from_email=from_email))
            except TemplateDoesNotExist as e:
                # Subject template does not exist.
                logger.warning('Subject template does not exist "%s"' % e)

            connection = get_connection(fail_silently=True)
            return connection.send_messages(messages)
        else:
            return 0
