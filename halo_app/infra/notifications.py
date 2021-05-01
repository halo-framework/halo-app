#pylint: disable=too-few-public-methods
import abc
import smtplib
import logging

from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class AbstractNotifications(abc.ABC):

    @abc.abstractmethod
    def send(self, destination, message):
        raise NotImplementedError


class EmailNotifications(AbstractNotifications):
    DEFAULT_HOST = None#settings.get_email_host_and_port()['host']
    DEFAULT_PORT = None#settings.get_email_host_and_port()['port']

    def __init__(self, smtp_host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.server = smtplib.SMTP(smtp_host, port=port)
        self.server.noop()

    def send(self, destination, message):
        msg = f'Subject: allocation service notification\n{message}'
        self.server.sendmail(
            from_addr='allocations@example.com',
            to_addrs=[destination],
            msg=msg
        )
