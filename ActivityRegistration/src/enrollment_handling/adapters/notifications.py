# pylint: disable=too-few-public-methods
import abc
import smtplib
from enrollment_handling import config
from dataclasses import asdict, dataclass
from mailjet_rest import Client


class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, destination, subject, message):
        raise NotImplementedError


DEFAULT_HOST = config.get_email_host_and_port()["host"]
DEFAULT_PORT = config.get_email_host_and_port()["port"]
DEFAULT_SENDER = config.get_email_host_and_port()['sender_email']


class EmailNotifications(AbstractNotifications):
    def __init__(self, smtp_host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.mjconfig = config.get_mj_credentials()
        if not self.mjconfig['use_mailjet']:
            self.server = smtplib.SMTP(smtp_host, port=port)
            self.server.noop()

    def send(self, destination, subject, message):
        msg = f"Subject: activity handler service notification\n{message}"

        if self.mjconfig['use_mailjet']:
            mailjet = Client(auth=(self.mjconfig['api_key'], self.mjconfig['private_key']), version='v3.1')
            email = MailjetMessages()
            email.Messages.append(
                MailjetMessage(send_from=DEFAULT_SENDER, send_to=destination, message=msg, subject=subject)
            )
            result = mailjet.send.create(data=asdict(email))
            print(result)
        else:
            self.server.sendmail(
                from_addr=DEFAULT_SENDER,
                to_addrs=[destination],
                msg=msg,
            )


@dataclass
class MailjetMessages:
    def __init__(self):
        self.Messages = []


@dataclass
class MailjetMessage:
    def __init__(self, send_from, send_to, subject, message):
        self.To = []
        if send_to:
            if isinstance(send_to, list):
                for to in send_to:
                    if isinstance(to, MailjetRecipient):
                        self.To.append(to)
                    elif '@' in to:
                        self.To.append(MailjetRecipient(to, to))
            elif '@' in send_to:
                self.To.append(MailjetRecipient(send_to, send_to))
            else:
                raise Exception(f'{send_to} is not valid!')
        else:
            raise Exception(f'No to email was sent!')

        if send_from:
            if isinstance(send_from, MailjetRecipient):
                self.From = send_from
            elif '@' in send_from:
                self.From = MailjetRecipient(send_from, send_from)
            else:
                raise Exception(f'{send_from} is not valid!')
        else:
            raise Exception(f'No from email was sent!')

        self.Subject = subject
        self.TextPart = message
        self.HtmlPart = message


@dataclass
class MailjetRecipient:
    def __init__(self, name, address):
        self.Email = address
        self.Name = name
