# -*- coding: utf-8 -*-
"""
    flaskext.mail
    ~~~~~~~~~~~~~

    Flask extension for sending email.

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement

from contextlib import contextmanager

from flaskext.mail.connection import Connection
from flaskext.mail.message import Message, Attachment, BadHeaderError
from flaskext.mail.signals import email_dispatched


class Mail(object):
    """
    Manages email messaging

    :param app: Flask instance
    """

    def __init__(self, app=None):
        
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

        self.server = app.config.get('MAIL_SERVER', '127.0.0.1')
        self.username = app.config.get('MAIL_USERNAME')
        self.password = app.config.get('MAIL_PASSWORD')
        self.port = app.config.get('MAIL_PORT', 25)
        self.use_tls = app.config.get('MAIL_USE_TLS', False)
        self.use_ssl = app.config.get('MAIL_USE_SSL', False)
        self.debug = int(app.config.get('MAIL_DEBUG', app.debug))
        self.max_emails = app.config.get('DEFAULT_MAX_EMAILS')
        self.suppress = app.config.get('MAIL_SUPPRESS_SEND', False)
        self.fail_silently = app.config.get('MAIL_FAIL_SILENTLY', True)

        self.suppress = self.suppress or app.testing
        self.app = app

        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mail'] = self


    @contextmanager
    def record_messages(self):
        """
        Records all messages. Use in unit tests for example::
            
            with mail.record_messages() as outbox:
                response = app.test_client.get("/email-sending-view/")
                assert len(outbox) == 1
                assert outbox[0].subject == "testing"

        You must have blinker installed in order to use this feature.
        :versionadded: 0.4
        """

        if not email_dispatched:
            raise RuntimeError, "blinker must be installed"
        
        outbox = []

        def _record(message, app):
            outbox.append(message)
        
        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)

    def send(self, message):
        """
        Sends a single message instance. If TESTING is True
        the message will not actually be sent.

        :param message: a Message instance.
        """

        with self.connect() as connection:
            message.send(connection)

    def send_message(self, *args, **kwargs):
        """
        Shortcut for send(msg). 

        Takes same arguments as Message constructor.
    
        :versionadded: 0.3.5
        """

        self.send(Message(*args, **kwargs))

    def connect(self, max_emails=None):
        """
        Opens a connection to the mail host.
        
        :param max_emails: the maximum number of emails that can 
                           be sent in a single connection. If this 
                           number is exceeded the Connection instance 
                           will reconnect to the mail server. The
                           DEFAULT_MAX_EMAILS config setting is used 
                           if this is None.
        """
        return Connection(self, max_emails) 
                          

