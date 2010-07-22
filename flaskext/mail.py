# -*- coding: utf-8 -*-
"""
    flaskext.mail
    ~~~~~~~~~~~~~

    Flask extension for sending email.

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from __future__ import with_statement

from flask import _request_ctx_stack

from lamson.server import Relay
from lamson.mail import MailResponse


class BadHeaderError(Exception): pass


class Connection(object):

    """Handles connection to host."""

    def __init__(self, mail, testing=False, send_many=False):

        self.mail = mail
        self.relay = mail.relay
        self.testing = testing
        self.send_many = send_many

    def __enter__(self):

        # if send_many, create a permanent connection to the host

        if self.send_many and not self.testing:
            self.host = self.relay.configure(self.relay.hostname)
        else:
            self.host = None
        
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.host:
            self.host.quit()

    def send_test_mail(self, message):

        outbox = getattr(_request_ctx_stack.top.g, 'outbox', [])
        outbox.append(message)

        _request_ctx_stack.top.g.outbox = outbox
    
    def send(self, message):
        """
        Sends message.
        
        :param message: Message instance.
        """
        if self.testing:
            self.send_test_mail(message)
        elif self.host:
            self.host.sendmail(message.sender,
                               message.recipients,
                               str(message.get_response()))
        else:
            self.relay.deliver(message.get_response())

    
class Mail(object):
    
    """
    Manages email messaging

    :param app: Flask instance
    """

    relay_class = Relay

    def __init__(self, app=None):
        self._relay = None
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initializes your mail settings from the application
        settings.

        You can use this if you want to set up your Mail instance
        at configuration time.

        :param app: Flask application instance
        """

        server = app.config.get('MAIL_SERVER', '127.0.0.1')
        username = app.config.get('MAIL_USERNAME')
        password = app.config.get('MAIL_PASSWORD')
        port = app.config.get('MAIL_PORT', 25)
        use_tls = app.config.get('MAIL_USE_TLS', False)
        use_ssl = app.config.get('MAIL_USE_SSL', False)
        debug = int(app.config.get('MAIL_DEBUG', app.debug))
    
        self.relay = self.relay_class(server, port, username, password,
            use_ssl, use_tls, debug)

        self.testing = app.config['TESTING']

        self.app = app

    def send(self, message):
        """
        Sends a single message instance. If TESTING then
        will add the message to **g.outbox**.

        :param message: a Message instance.
        """

        with self.connect(send_many=False) as connection:
            message.send(connection)

    def connect(self, send_many=True):
        """
        Opens a connection to the mail host.
        
        :param send_many: keep connection alive
        """
        return Connection(self, 
                          send_many=send_many, 
                          testing=self.testing)


class Message(object):
    
    """
    Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address, or **DEFAULT_MAIL_SENDER** by default
    """

    def __init__(self, subject, 
                 recipients=None, 
                 body=None, 
                 html=None, 
                 sender=None):


        if sender is None:
            app = _request_ctx_stack.top.app
            sender = app.config.get("DEFAULT_MAIL_SENDER")

        if isinstance(sender, tuple):
            # sender can be tuple of (name, address)
            sender = "%s <%s>" % sender

        self.subject = subject
        self.sender = sender
        self.body = body
        self.html = html

        if recipients is None:
            recipients = []

        self.recipients = list(recipients)
        
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
        
    def send(self, connection):
        """
        Verifies and sends the message.
        """
        
        assert self.recipients, "No recipients have been added"
        assert self.body or self.html, "No body or HTML has been set"
        assert self.sender, "No sender address has been set"

        if self.is_bad_headers():
            raise BadHeaderError

        connection.send(self)

    def add_recipient(self, recipient):
        """
        Adds another recipient to the message.
        
        :param recipient: email address of recipient.
        """
        
        self.recipients.append(recipient)

    def attach(self, 
               filename=None, 
               content_type=None, 
               data=None,
               disposition=None):
        
        """
        Adds an attachment to the message.
        
        :param filename: filename of attachment
        :param content_type: file mimetype
        :param data: the raw file data
        :param disposition: content-disposition (if any)
        """

        self.attachments.append((filename, 
                                 content_type, 
                                 data, 
                                 disposition))

