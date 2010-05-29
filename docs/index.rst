.. flask-mail documentation master file, created by
   sphinx-quickstart on Fri May 28 11:39:14 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to flask-mail's documentation!
======================================

One of the most basic functions in a web application is the ability to send
emails to your users.

The flask-mail extension provides a simple interface to set up SMTP with your
application and to send messages from views.

This extension requires the `Lamson email library <http://lamsonproject.org>`_.

Installing flask-mail
---------------------

Download the latest version from Bitbucket:

    hg clone http://bitbucket.org/danjac/flask-mail
    cd flask-mail
    python setup.py install

If you are using `virtualenv`, it is assumed that you are installing flask-mail
in the same virtualenv as your Flask application(s).

Configuring flask-mail
----------------------

Flask-mail is configured through the standard Flask configuration options.

The following are the various configuration settings you need to know:

MAIL_SERVER : default 'localhost'
MAIL_PORT : default 25
MAIL_USE_TLS : default False
MAIL_USE_SSL : default False
MAIL_DEBUG : default app.debug
MAIL_USERNAME : default None
MAIL_PASSWORD : default None
MAIL_TEST_ENV : default False
DEFAULT_MAIL_SENDER : default None

To set up flask-ext with your application use the `init_mail` function:

    from flask import Flask
    from flaskext.mail import init_mail

    app = Flask(__name__)
    init_mail(app)

Under the hood
--------------

The `init_mail` function creates a Lamson `Relay` instance, which is attached
to the application instance as mail_relay. Most of the time you should
not need to access the relay directly.

Sending messages
----------------

To send a message first create a `Message` instance:

    from flaskext.mail import Message

    @app.route("/")
    def index():

        msg = Message("Hello",
                      recipients="to@example.com")
        
You can set the recipients immediately, or individually:

    msg.add_recipient("somebodyelse@example.com")

If you have set `DEFAULT_MAIL_SENDER` you don't need to set the message
sender explicity, as it will use this configuration value by default.

The message can contain a body and/or HTML:

    msg.body = "testing"
    msg.html = "<b>testing</b>"

Finally just send the message:

    msg.send()

You can pass another `Relay` instance if you need to (for example, you might
use another mail server for mailing lists):

    from lamson.server import Relay
    another_relay = Relay()
    msg.send(another_relay)

Attachments
-----------

It's simple to add attachments:

    msg.attach(filename, content_type, data)

For example:

    with app.open_resource("image.png") as fp:
        msg.attach("image.png", "image/png", fp.read())

Logging
-------

TBD

Unit tests
----------

When you are sending messages inside of unit tests, or in a development
environment, it's useful to be able to suppress emails. 

If the setting `MAIL_TEST_ENV` is set to True, emails will be
suppressed. Calling `send()` on your messages will not result in 
any messages being sent.

However, it's still useful to track in  your unit tests which 
mails have been sent their details.

When `MAIL_TEST_ENV` is on, an "outbox" list is attached to the
thread local `g` object, so you can then inspect what emails are sent
(or would be sent in full production):

    assert g.outbox[0].subject == "testing"

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

