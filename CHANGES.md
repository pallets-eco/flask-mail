## Version 0.10.0

Unreleased

-   Drop support for Python < 3.8.
-   Use `pyproject.toml` for packaging metadata.
-   Use `flit_core` as build backend.
-   Apply code formatting and linting tools.
-   Deprecate the `__version__` attribute. Use feature detection or
    `importlib.metadata.version("flask-mail")` instead.
-   Indicate that the deprecated `is_bad_headers` will be removed in the next
    version.
-   Fix the `email_dispatched` signal to pass the current app as the sender and
    `message` as an argument, rather than the other way around.


## Version 0.9.1

Released 2014-09-28

-   Add an option for force ASCII file attachments
-   Fix `force_text` function
-   Fix some Python 3 support regarding email policy.
-   Support ESMTP options.
-   Fix various Unicode issues related to message attachments, subjects, and
    email addresses.


## Version 0.9.0

Released 2013-06-14

-   Add initial Python 3 support.


## Version 0.8.2

Released 2013-04-11

-   Remove stray `print` statement.


## Version 0.8.1

Released 2013-04-04

-   Fix a bug with the new state object.


## Version 0.8.0

Released 2013-04-03

-   Fix a bug with duplicate recipients.
-   Change configuration options to be less confusing. Update settings accordin
    ly:
    -   `DEFAULT_MAIL_SENDER` is now `MAIL_DEFAULT_SENDER`.
    -   `DEFAULT_MAX_EMAILS` is now `MAIL_MAX_EMAILS`.
    -   `MAIL_FAIL_SILENTLY` is no longer used.
    -   `MAIL_SUPPRESS_SEND` now defaults to `TESTING` setting value.
-   General API cleanup as things were happening in a few different places.


## Version 0.7.6

Released 2013-03-11

-   Fix bug with cc, and bcc fields not being lists.


## Version 0.7.5

Released 2013-03-03

-   Fix bug with non-ascii characters in email address.
-   `MAIL_FAIL_SILENTLY` config value defaults to `False`.
-   Bcc header no longer set as some mail servers forward it to the recipient.


## Version 0.7.4

Released 2012-11-20

-   Allow messages to be sent without a body.


## Version 0.7.3

Released 2012-09-27

-   Add `extra_headers` to `Message` class.


## Version 0.7.2

Released 2012-09-16

-   Add `__str__` method to `Message` class.
-   Add message character set option which defaults to utf-8.


## Version 0.7.1

Released 2012-09-05

-   Date and message ID headers specified.


## Version 0.7.0

Released 2012-08-29

-   Initial development by Dan Jacob and Ron DuPlain. Previously there was not a
    change log.
