#:coding=utf8:


class BaseBackend(object):

    def send(self, targets, notify_type, media, extra_data={}):
        """
        Sends a message to the given users.

        targets: The notification target model instance. Normally a user.
        notify_type: The notify type
        media: The media name
        extra_context: A dictionary containing extra data that is sent along with
                       the notification
        Returns the number of notifications sent.
        """
        num_sent = 0
        for target in targets:
            num_sent += self._send(
                target=target,
                notify_type=notify_type,
                media=media,
                extra_data=extra_data,
            )
        return num_sent

    def _send(self, target, notify_type, media, extra_data={}):
        raise NotImplementedError("You must implement the _send() method in "
                                  "from the BaseBackend class.")

    def get(self, target, media, start=None, end=None):
        """
        Retrieves notifications for the target from the
        backend for the given media. The backend should
        return notifications in the order they were sent
        if possible.

        If given a start or end index the backend should return only
        the notifications within the given range. If no start index
        is given then the backend should return the first available
        notification. If no end index is given then the backend
        should return up to the last available notification.

        The backend should return the notifications in the format
        of an iterable of python dictionaries of the format described below:

        notifications = [
            {
                'target': target,
                'notify_type': notify_type,
                'media': media,
                'extra_data': {
                    'spam': 'eggs',
                }
                'ctime': datetime.datetime(...),
            },
            ...
        ]
        """
        raise NotImplementedError('This backend does not support retrieving notifications.')

    def count(self, target, media):
        """
        Retrieves then number of notifications for the target from the backend
        for the given media. The backend should return notifications in the
        order they were sent if possible.
        """
        raise NotImplementedError('This backend does not support retrieving counts.')
