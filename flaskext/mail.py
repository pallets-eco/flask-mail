"""
    flaskext.mail
    ~~~~~~~~~~~~~

    Flask extension for sending email.

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""

from flask import current_app, LocalProxy

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
    
    The relay object is appended to the application instance
    as mail_relay and to a LocalProxy object as 'relay'. You
    can use this with a Lamson MailResponse instance to send 
    more complex emails, or just use the send() method:

    from flaskext.mail import relay, MailResponse

    @app.route("/")
    def index():
        
        msg = MailResponse(subject)
        relay.deliver(msg)
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

relay = LocalProxy(lambda: current_app.mail_relay)




