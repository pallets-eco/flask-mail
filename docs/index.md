# Flask-Mail

```{currentmodule} flask-mail
```

One of the most basic functions in a web application is the ability to send
emails to your users.

The Flask-Mail extension provides a simple interface to set up SMTP with your
[Flask] application and to send messages from your views and scripts.

[flask]: https://flask.palletsprojects.com

```{toctree}
:hidden:

api
changes
license
```


## Installing

Install from PyPI using an installer such as pip:

```sh
$ pip install Flask-Mail
```


## Configuring

Flask-Mail is configured through the standard Flask config API. These are the
available  options (each is explained later in the documentation):

```{data} MAIL_SERVER
:type: str
:value: 'localhost'
```

```{data} MAIL_PORT
:type: int
:value: 25
```

```{data} MAIL_USE_TLS
:type: bool
:value: False
```

```{data} MAIL_USE_SSL
:type: bool
:value: False
```

```{data} MAIL_DEBUG
:type: bool
:value: app.debug
```

```{data} MAIL_USERNAME
:type: str | None
:value: None
```

```{data} MAIL_PASSWORD
:type: str | None
:value: None
```

```{data} MAIL_DEFAULT_SENDER
:type: str | None
:value: None
```

```{data} MAIL_MAX_EMAILS
:type: int | None
:value: None
```

```{data} MAIL_SUPPRESS_SEND
:type: bool
:value: app.testing
```

```{data} MAIL_ASCII_ATTACHMENTS
:type: bool
:value: False
```

In addition, the standard Flask `TESTING` configuration option is used by
Flask-Mail in unit tests (see below).


## The extension instance

Emails are managed through a {class}`.Mail` instance:

```py
from flask import Flask
from flask_mail import Mail

app = Flask(__name__)
mail = Mail(app)
```

In this case all emails are sent using the configuration values of the
application that was passed to the {class}`.Mail` class constructor.

Alternatively you can set up your {class}`.Mail` instance later at configuration
time, using the {meth}`~.Mail.init_app` method:

```py
mail = Mail()

app = Flask(__name__)
mail.init_app(app)
```

In this case emails will be sent using the configuration values from Flask's
{data}`~flask.current_app` context global. This is useful if you have
multiple applications running in the same process but with different
configuration options.

```{admonition} Load email configuration
Note that Flask-Mail needs the configuration parameters to create a mail
handler, so you have to make sure to load your configuration before the
initialization of Flask-Mail (either using {class}`Mail` constructor or
{meth}`~.Mail.init_app` method).
```


## Sending messages

To send a message first create a {class}`.Message` instance:

```py
from flask_mail import Message

@app.route("/")
def index():
    msg = Message(
        subject="Hello",
        sender="from@example.com",
        recipients=["to@example.com"],
    )
```

You can set the recipient emails immediately, or individually:

```py
msg.recipients = ["you@example.com"]
msg.add_recipient("somebodyelse@example.com")
```

If you have set {data}`.MAIL_DEFAULT_SENDER` you don't need to set the message sender
explicity, as it will use this configuration value by default:

```py
msg = Message(
    subject="Hello",
    recipients=["to@example.com"],
)
```

If the `sender` is a two-element tuple, this will be split into name and address:

```py
msg = Message(
    subject="Hello",
    sender=("Me", "me@example.com"),
)
assert msg.sender == "Me <me@example.com>"
```

The message can contain a body and/or HTML:

```py
msg.body = "testing"
msg.html = "<b>testing</b>"
```

Finally, to send the message, you use the {class}`.Mail` instance configured
with your Flask application:

```py
mail.send(msg)
```


## Bulk emails

Usually in a web application you will be sending one or two emails per request.
In certain situations you might want to be able to send perhaps dozens or
hundreds of emails in a single batch - probably in an external process such as a
command-line script or cronjob.

In that case you do things slightly differently:

```py
with mail.connect() as conn:
    for user in users:
        msg = Message(
            subject=f"hello, {user.name}",
            body="...",
            recipients=[user.email],
        )
        conn.send(msg)
```

The connection to your email host is kept alive and closed automatically once
all the messages have been sent.

Some mail servers set a limit on the number of emails sent in a single
connection. You can set the max amount of emails to send before reconnecting by
specifying the {data}`.MAIL_MAX_EMAILS` setting.


## Attachments

Adding attachments is straightforward:

```py
with app.open_resource("image.png") as fp:
    msg.attach("image.png", "image/png", fp.read())
```

If {data}`.MAIL_ASCII_ATTACHMENTS` is set to `True`, filenames will be converted
to an ASCII equivalent. This can be useful when using a mail relay that modify mail
content and mess up Content-Disposition specification when filenames are UTF-8
encoded. The conversion to ASCII is a basic removal of non-ASCII characters. It
should be fine for any unicode character that can be decomposed by NFKD into one
or more ASCII characters. If you need romanization/transliteration (i.e `ß` →
`ss`) then your application should do it and pass a proper ASCII string.


## Unit tests and suppressing emails

When you are sending messages inside unit tests, or in a development
environment, it's useful to be able to suppress email sending.

If the setting `TESTING` is set to `True`, emails will be suppressed. Calling
{meth}`Message.send` will not result in any messages being actually sent.

Alternatively outside a testing environment you can set
{data}`.MAIL_SUPPRESS_SEND` to `True`. This will have the same effect.

However, it's still useful to keep track of emails that would have been sent
when you are writing unit tests.

In order to keep track of dispatched emails, use the {meth}`~.Mail.record_messages`
method:

```py
with mail.record_messages() as outbox:
    mail.send_message(
        subject="testing",
        body="test",
        recipients=emails,
    )
    assert len(outbox) == 1
    assert outbox[0].subject == "testing"
```

The `outbox` is a list of {class}`.Message` instances sent.


## Header injection

To prevent header injection, attempts to send a message with newlines in the
subject, sender or recipient addresses will result in a `BadHeaderError`.


## Signalling support

Flask-Mail provides signalling support through a {data}`.email_dispatched`
signal. This is sent whenever an email is dispatched (even if the email is not
actually sent, i.e. in a testing environment).

A function connecting to the {data}`.email_dispatched` signal is sent with the
{class}`~flask.Flask` instance as the first argument, and the {class}`.Message}`
instance as the `message` argument.

```py
def log_message(app, message):
    app.logger.debug(message.subject)

email_dispatched.connect(log_message)
```
