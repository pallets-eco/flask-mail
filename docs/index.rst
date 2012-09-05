flask-mail
======================================

.. module:: flask-mail

One of the most basic functions in a web application is the ability to send
emails to your users.

The **Flask-Mail** extension provides a simple interface to set up SMTP with your
`Flask`_ application and to send messages from your views and scripts.

Links
-----

* `documentation <http://packages.python.org/Flask-Mail/>`_
* `source <http://github.com/mattupstate/flask-mail>`_
* :doc:`changelog </changelog>`

Installing Flask-Mail
---------------------

Install with **pip** and **easy_install**::

    pip install Flask-Mail

or download the latest version from version control::

    git clone https://github.com/rduplain/flask-mail.git
    cd flask-mail
    python setup.py install

If you are using **virtualenv**, it is assumed that you are installing flask-mail
in the same virtualenv as your Flask application(s).

Configuring Flask-Mail
----------------------

**Flask-Mail** is configured through the standard Flask config API. These are the available
options (each is explained later in the documentation):

* **MAIL_SERVER** : default **'localhost'**

* **MAIL_PORT** : default **25**

* **MAIL_USE_TLS** : default **False**

* **MAIL_USE_SSL** : default **False**

* **MAIL_DEBUG** : default **app.debug**

* **MAIL_USERNAME** : default **None**

* **MAIL_PASSWORD** : default **None**

* **DEFAULT_MAIL_SENDER** : default **None**

* **DEFAULT_MAX_EMAILS** : default **None**

* **MAIL_FAIL_SILENTLY** : default **True**

* **MAIL_SUPPRESS_SEND** : default **False**
git
In addition the standard Flask ``TESTING`` configuration option is used by **Flask-Mail**
in unit tests (see below).

Emails are managed through a ``Mail`` instance::

    from flask import Flask
    from flask_mail import Mail

    app = Flask(__name__)
    mail = Mail(app)

Alternatively you can set up your ``Mail`` instance later at configuration time, using the
**init_app** method::

    mail = Mail()

    app = Flask(__name__)
    mail.init_app(app)


Sending messages
----------------

To send a message first create a ``Message`` instance::

    from flask_mail import Message

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

If the ``sender`` is a two-element tuple, this will be split into name
and address::

    msg = Message("Hello",
                  sender=("Me", "me@example.com"))

    assert msg.sender == "Me <me@example.com>"

The message can contain a body and/or HTML::

    msg.body = "testing"
    msg.html = "<b>testing</b>"

Finally, to send the message, you use the ``Mail`` instance configured with your Flask application::

    mail.send(msg)

If the setting **MAIL_FAIL_SILENTLY** is **True**, and the connection fails (for example, the mail
server cannot be found at that hostname) then no error will be raised, although of course no emails will
be sent either.


Bulk emails
-----------

Usually in a web application you will be sending one or two emails per request. In certain situations
you might want to be able to send perhaps dozens or hundreds of emails in a single batch - probably in
an external process such as a command-line script or cronjob.

In that case you do things slightly differently::

    with mail.connect() as conn:
        for user in users:
            message = '...'
            subject = "hello, %s" % user.name
            msg = Message(recipients=[user.email],
                          body=message,
                          subject=subject)

            conn.send(msg)


The connection to your email host is kept alive and closed automatically once all the messages have been sent.

If you are going to run a mass email batch, be careful to pass in the ``max_emails`` parameter, which sets the maximum
number of emails that will be sent before reconnecting. Some mail servers set a limit on the number of emails sent
in a single connection. You can also set this globally with the **DEFAULT_MAX_EMAILS** setting.

Attachments
-----------

Adding attachments is straightforward::

    with app.open_resource("image.png") as fp:
        msg.attach("image.png", "image/png", fp.read())

See the `API`_ for details.

Unit tests and suppressing emails
---------------------------------

When you are sending messages inside of unit tests, or in a development
environment, it's useful to be able to suppress email sending.

If the setting ``TESTING`` is set to ``True``, emails will be
suppressed. Calling ``send()`` on your messages will not result in
any messages being actually sent.

Alternatively outside a testing environment you can set ``MAIL_SUPPRESS_SEND`` to **False**. This
will have the same effect.

However, it's still useful to keep track of emails that would have been
sent when you are writing unit tests.

In order to keep track of dispatched emails, use the ``record_messages``
method::

    with mail.record_messages() as outbox:

        mail.send_message(subject='testing',
                          body='test',
                          recipients=emails)

        assert len(outbox) == 1
        assert outbox[0].subject == "testing"

The **outbox** is a list of ``Message`` instances sent.

The blinker package must be installed for this method to work.

Note that the older way of doing things, appending the **outbox** to
the ``g`` object, is now deprecated.


Header injection
----------------

To prevent `header injection <http://www.nyphp.org/PHundamentals/8_Preventing-Email-Header-Injection>`_ attempts to send
a message with newlines in the subject, sender or recipient addresses will result in a ``BadHeaderError``.

Signalling support
------------------

.. versionadded:: 0.4

**Flask-Mail** now provides signalling support through a ``email_dispatched`` signal. This is sent whenever an email is
dispatched (even if the email is not actually sent, i.e. in a testing environment).

A function connecting to the ``email_dispatched`` signal takes a ``Message`` instance as a first argument, and the Flask
app instance as an optional argument::

    def log_message(message, app):
        app.logger.debug(message.subject)

    email_dispatched.connect(log_message)


API
---

.. module:: flask_mail

.. autoclass:: Mail
   :members: send, connect, send_message

.. autoclass:: Attachment

.. autoclass:: Connection
   :members: send, send_message

.. autoclass:: Message
   :members: attach, add_recipient

.. _Flask: http://flask.pocoo.org
.. _GitHub: http://github.com/rduplain/flask-mail
