"""
    flaskext.mail
    ~~~~~~~~~~~~~

    Flask extension for sending email.

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""

from flask import current_app

from lamson.server import Relay
from lamson.mail import MailResponse

def init_mail(app):
    """
    Initializes a Lamson Relay object. 

    The following configuration options can be passed in the 
    Flask configuration file:

    MAIL_SERVER : default 'localhost'
    MAIL_PORT : default 25
    MAIL_USE_TLS : default False
    MAIL_USE_SSL : default False
    MAIL_DEBUG : default app.debug
    MAIL_USERNAME : default None
    MAIL_PASSWORD : default None
    DEFAULT_MAIL_SENDER : default None
    
    The relay object is appended to the application instance
    as mail_relay and to a LocalProxy object as 'relay'. You
    can use this with a Lamson MailResponse instance to send 
    more complex emails, or just use the send() method:

    from flaskext.mail import Message

    @app.route("/")
    def index():
        
        msg = Message
        relay.deliver(subject="hello", body="hello world",
                      recipients=["me@mysite.com"])
    """
    
    server = app.config.get('MAIL_SERVER', '127.0.0.1')
    username = app.config.get('MAIL_USERNAME')
    password = app.config.get('MAIL_PASSWORD')
    port = app.config.get('MAIL_PORT', 25)
    use_tls = app.config.get('MAIL_USE_TLS', False)
    use_ssl = app.config.get('MAIL_USE_SSL', False)
    debug = int(app.config.get('MAIL_DEBUG', app.debug))

    app.mail_relay = Relay(server, 
                           port,
                           username, 
                           password,
                           use_ssl,
                           use_tls,
                           debug)


class Message(object):

    def __init__(self, subject, recipients, body=None, html=None, sender=None):
        
        if sender is None:
            sender = current_app.config.get("DEFAULT_MAIL_SENDER")

        if sender is None:
            raise ValueError, "sender not provided nor is DEFAULT_MAIL_SENDER set"

        self.subject = subject
        self.sender = sender
        self.body = body
        self.html = html

        if isinstance(recipients, basestring):
            self.recipients = [recipients]

        self.attachments = []

    def get_response(self):
        """
        Creates a Lamson MailResponse instance
        """

        response = MailResponse(Subject=self.subject, 
                                To=self.recipients,
                                From=self.sender,
                                Body=self.body,
                                Html=self.html)

        for filename, content_type, data, disp in self.attachments:

            response.attach(filename, content_type, data, disp)

        return response

    def send(self, relay=None):

        if relay is None:

            relay = current_app.mail_relay

        relay.deliver(self.get_response())

    def add_recipient(self, recipient):
        
        self.recipients.append(recipient)

    def attach(self, 
               filename=None, 
               content_type=None, 
               data=None,
               disposition=None):

        self.attachments.append((filename, content_type, data, disposition))

