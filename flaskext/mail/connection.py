import smtplib
import socket

from flaskext.mail.message import Message
from flaskext.mail.signals import email_dispatched

class Connection(object):

    """Handles connection to host."""

    def __init__(self, mail, max_emails=None):

        self.mail = mail
        self.app = self.mail.app
        self.testing = self.app.testing
        self.max_emails = max_emails or self.mail.max_emails or 0
        self.fail_silently = self.mail.fail_silently

    def __enter__(self):

        if self.testing:
            self.host = None
        else:
            self.host = self.configure_host()
        
        self.num_emails = 0

        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.host:
            self.host.quit()
    
    def configure_host(self):
        
        try:
            if self.mail.use_ssl:
                host = smtplib.SMTP_SSL(self.mail.server, self.mail.port)
            else:
                host = smtplib.SMTP(self.mail.server, self.mail.port)
        except socket.error:
            if self.fail_silently:
                return
            raise

        host.set_debuglevel(int(self.app.debug))

        if self.mail.use_tls:
            host.starttls()
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)

        return host

    def send(self, message):
        """
        Sends message.
        
        :param message: Message instance.
        """

        if self.host:
            self.host.sendmail(message.sender,
                               message.recipients,
                               str(message.get_response()))
        

        if email_dispatched:
            email_dispatched.send(message, app=self.app)

        self.num_emails += 1

        if self.num_emails == self.max_emails:
            
            self.num_emails = 0
            if self.host:
                self.host.quit()
                self.host = self.configure_host()

    def send_message(self, *args, **kwargs):
        """
        Shortcut for send(msg). 

        Takes same arguments as Message constructor.
    
        :versionadded: 0.3.5

        """

        self.send(Message(*args, **kwargs))


