# API

Anything documented here is part of the public API that Flask-Mail provides,
unless otherwise indicated. Anything not documented here is considered internal
or private and may change at any time.

```{eval-rst}
.. module:: flask_mail

.. autoclass:: Mail
    :members: init_app, send, connect, send_message

.. autoclass:: Attachment

.. autoclass:: Connection
    :members: send, send_message

.. autoclass:: Message
    :members: attach, add_recipient

.. autodata:: email_dispatched
    :annotation:
```
