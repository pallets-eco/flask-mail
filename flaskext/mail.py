# -*- coding: utf-8 -*-
"""
    flaskext.mail
    ~~~~~~~~~~~~~

    Flask extension for sending email.

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""

from flask import current_app, g

from lamson.server import Relay as LamsonRelay
from lamson.mail import MailResponse

class BadHeaderError(Exception): pass


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
    MAIL_BATCH_SIZE : default None
    DEFAULT_MAIL_SENDER : default None
    
    The relay object is appended to the application instance
    as mail_relay and to a LocalProxy object as 'relay'. You
    can use this with a Lamson MailResponse instance to send 
    more complex emails, or just use the send() method:

    from flaskext.mail import Message

    @app.route("/")
    def index():
        
        msg = Message(subject="hello", 
                      body="hello world",
                      recipients=["me@mysite.com"])

        msg.send()

    If DEFAULT_MAIL_SENDER is set this will be used for 
    the sender address if no sender set.

    If you set TESTING to True:

    1) no emails are actually sent
    2) messages are added to a list in the g object, "outbox"

    This is useful for unit tests where you do not want
    to actually access a mail server, but you still want to
    track emails sent under test conditions.
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


class Relay(LamsonRelay):
    """
    Subclass of base Lamson Relay class, which includes
    some extra functionality.
    """

    def send_many(self, messages, batch_size=None):
        """
        Sends many messages, re-using the same connection.
        The batch_size parameter determines the max number 
        of messages sent with an open connection; when this is
        exceeded the connection is closed and re-opened.

        If batch_size is None then the MAIL_BATCH_SIZE config
        setting is used; if that is also None (default) then 
        no batch limit is set.
        """
        
        if current_app.config.get("TESTING", False):
            # just send as normal, as they won't really get sent
            for message in messages:
                message.send(relay=self)
            return

        if batch_size is None:
            batch_size = current_app.config.get("MAIL_BATCH_SIZE", None)
            if batch_size is None:
                batch_size = len(messages)

        relay_host = None

        for counter, message in enumerate(messages, 1):
            if relay_host is None:
                relay_host = self.configure_relay(self.hostname)

            relay_host.sendmail(message.sender, 
                                message.recipients, 
                                str(message.get_response()))
        

            if counter == batch_size:
                relay_host.quit()
                relay_host = None

        # ensure connection closed

        if relay_host is not None:
            relay_host.quit()


class Message(object):

    def __init__(self, subject, 
                 recipients=None, 
                 body=None, 
                 html=None, 
                 sender=None):
        
        if sender is None:
            sender = current_app.config.get("DEFAULT_MAIL_SENDER")

        if isinstance(sender, tuple):
            # sender can be tuple of (name, address)
            sender = "%s <%s>" % sender

        self.subject = subject
        self.sender = sender
        self.body = body
        self.html = html

        if recipients is None:
            recipients = []

        self.recipients = recipients
        
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
    
    def is_bad_headers(self):
        """
        Checks for bad headers i.e. newlines in subject, sender or recipients.
        """
       
        for val in [self.subject, self.sender] + self.recipients:
            for c in '\r\n':
                if c in val:
                    return True
        return False
        
    def send(self, relay=None):
        
        assert self.recipients, "No recipients have been added"
        assert self.body or self.html, "No body or HTML has been set"
        assert self.sender, "No sender address has been set"

        if self.is_bad_headers():
            raise BadHeaderError

        if current_app.config.get("TESTING", False):
            
            outbox = getattr(g, 'outbox', [])
            outbox.append(self)
            g.outbox = outbox
            return

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

        self.attachments.append((filename, 
                                 content_type, 
                                 data, 
                                 disposition))

