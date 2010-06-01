flask-mail
======================================

.. module:: flask-mail

One of the most basic functions in a web application is the ability to send
emails to your users.

The **flask-mail** extension provides a simple interface to set up SMTP with your
`Flask`_ application and to send messages from views.

This extension requires the `Lamson email library <http://lamsonproject.org>`_.

Source code and issue tracking at `Bitbucket`_.

Installing flask-mail
---------------------

Install with **pip** and **easy_install**::

    pip install flask-mail

or download the latest version from Bitbucket::

    hg clone http://bitbucket.org/danjac/flask-mail

    cd flask-mail

    python setup.py install

If you are using **virtualenv**, it is assumed that you are installing flask-mail
in the same virtualenv as your Flask application(s).

Configuring flask-mail
----------------------

Flask-mail is configured through the standard Flask configuration options:

* ``MAIL_SERVER`` : default ``'localhost'``

* ``MAIL_PORT`` : default ``25``

* ``MAIL_USE_TLS`` : default ``False``

* ``MAIL_USE_SSL`` : default ``False``

* ``MAIL_DEBUG`` : default ``app.debug``

* ``MAIL_USERNAME`` : default ``None``

* ``MAIL_PASSWORD`` : default ``None``

* ``MAIL_TEST_ENV`` : default ``False``

* ``DEFAULT_MAIL_SENDER`` : default ``None``

To set up flask-ext with your application use the ``init_mail`` function::

    from flask import Flask
    from flaskext.mail import init_mail

    app = Flask(__name__)
    init_mail(app)

Under the hood
--------------

The ``init_mail`` function creates a Lamson ``Relay`` instance, which is attached
to the application instance as ``mail_relay``. Most of the time you should
not need to access the relay directly::

    app = Flask(__name__)
    init_mail(app)
    assert app.mail_relay

Sending messages
----------------

To send a message first create a ``Message`` instance::

    from flaskext.mail import Message

    @app.route("/")
    def index():

        msg = Message("Hello",
                      sender="from@example.com",
                      recipients=["to@example.com"])
       
You can set the recipient emails immediately, or individually::

    msg.recipients = ["you@example.com"]
    msg.add_recipient("somebodyelse@example.com")

If you have set ``DEFAULT_MAIL_SENDER`` you don't need to set the message
sender explicity, as it will use this configuration value by default::

    msg = Message("Hello",
                  recipients=["to@example.com"])

The message can contain a body and/or HTML::

    msg.body = "testing"
    msg.html = "<b>testing</b>"

Finally just send the message::

    msg.send()

You can pass another ``Relay`` instance if you need to (for example, you might
use another mail server for newsletters)::

    from lamson.server import Relay

    another_relay = Relay(another_host)
    msg.send(another_relay)

Attachments
-----------

Adding attachments is straightforward::

    with app.open_resource("image.png") as fp:
        msg.attach("image.png", "image/png", fp.read())

See the API for details.

Unit tests
----------

When you are sending messages inside of unit tests, or in a development
environment, it's useful to be able to suppress email sending (although you can
also set up Lamson as a test mail server on your local machine - see the
Lamson documentation for details).

If the setting ``MAIL_TEST_ENV`` is set to ``True``, emails will be
suppressed. Calling ``send()`` on your messages will not result in 
any messages being sent.

However, it's still useful to track in  your unit tests which 
emails have been sent.

When ``MAIL_TEST_ENV`` is on, an ``outbox`` list is attached to the
thread local ``g`` object, so you can then inspect what emails are sent
(or would be sent in production mode)::

    assert g.outbox[0].subject == "testing"

API
---

.. module:: flaskext.mail

.. function:: init_mail(app)

    Initializes the mail extension. Attaches a Lamson ``Relay`` instance to the Flask application as ``mail_relay``.

    Uses the following Flask configuration values:

    * ``MAIL_SERVER`` : default ``'localhost'``

    * ``MAIL_PORT`` : default ``25``

    * ``MAIL_USE_TLS`` : default ``False``

    * ``MAIL_USE_SSL`` : default ``False``

    * ``MAIL_DEBUG`` : default ``app.debug``

    * ``MAIL_USERNAME`` : default ``None``

    * ``MAIL_PASSWORD`` : default ``None``

    * ``MAIL_TEST_ENV`` : default ``False``

    * ``DEFAULT_MAIL_SENDER`` : default ``None``

    The ``smtplib`` `debug level <http://docs.python.org/library/smtplib.html#smtplib.SMTP.set_debuglevel>`_ will be set to the value of ``MAIL_DEBUG``.  
    
    :param app: Flask application instance

.. class:: Message

    .. method:: __init__(subject, recipients=[], body=None, html=None, sender=None)

    :param subject: subject of the email message
    :param recipients: email recipients list
    :param body: body of email
    :param html: HTML part of email
    :param sender: from address (uses ``DEFAULT_MAIL_SENDER`` by default)

    .. method:: add_recipient(recipient)
    
    Adds another email address to the ``recipients`` list.

    :param recipient: email address of recipient
    
    .. method:: attach(filename, content_type, data, disposition=None)

    Adds an attachment to the message, for example::

        with app.open_resource("image.png") as fp:
            msg.attach("image.png", "image/png", fp.read())

    :param filename: name given to the attachment
    :param content_type: attachment mimetype
    :param data: data to be attached
    :param disposition: content disposition

    .. method:: send(relay=None):

    Sends the message. If ``MAIL_TEST_ENV`` is ``True`` then does not actually send the
    message, instead the message is added to the global object as ``g.outbox``.
    
    :param relay: Lamson ``Relay`` instance, uses ``app.mail_relay`` by default.

.. _Flask: http://flask.pocoo.org
.. _Bitbucket: http://bitbucket.org/danjac/flask-mail
