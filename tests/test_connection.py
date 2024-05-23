from __future__ import annotations

from unittest import mock

import pytest
from flask import Flask

from flask_mail import BadHeaderError
from flask_mail import Mail
from flask_mail import Message


def test_send_message(app: Flask, mail: Mail) -> None:
    with mail.record_messages() as outbox:
        with mail.connect() as conn:
            conn.send_message(
                subject="testing", recipients=["to@example.com"], body="testing"
            )
        assert len(outbox) == 1
        sent_msg = outbox[0]
        assert sent_msg.sender == app.extensions["mail"].default_sender


def test_send_single(app: Flask, mail: Mail) -> None:
    with mail.record_messages() as outbox:
        with mail.connect() as conn:
            msg = Message(
                subject="testing", recipients=["to@example.com"], body="testing"
            )
            conn.send(msg)
        assert len(outbox) == 1
        sent_msg = outbox[0]
        assert sent_msg.subject == "testing"
        assert sent_msg.recipients == ["to@example.com"]
        assert sent_msg.body == "testing"
        assert sent_msg.sender == app.extensions["mail"].default_sender


def test_send_many(app: Flask, mail: Mail) -> None:
    with mail.record_messages() as outbox:
        with mail.connect() as conn:
            for _i in range(100):
                msg = Message(
                    subject="testing", recipients=["to@example.com"], body="testing"
                )
                conn.send(msg)
        assert len(outbox) == 100
        sent_msg = outbox[0]
        assert sent_msg.sender == app.extensions["mail"].default_sender


def test_send_without_sender(app: Flask, mail: Mail) -> None:
    app.extensions["mail"].default_sender = None
    msg = Message(subject="testing", recipients=["to@example.com"], body="testing")
    with mail.connect() as conn:
        with pytest.raises(AssertionError):
            conn.send(msg)


def test_send_without_recipients(mail: Mail) -> None:
    msg = Message(subject="testing", recipients=[], body="testing")
    with mail.connect() as conn:
        with pytest.raises(AssertionError):
            conn.send(msg)


def test_bad_header_subject(mail: Mail) -> None:
    msg = Message(subject="testing\n\r", body="testing", recipients=["to@example.com"])
    with mail.connect() as conn:
        with pytest.raises(BadHeaderError):
            conn.send(msg)


def test_sendmail_with_ascii_recipient(mail: Mail) -> None:
    with mail.connect() as conn:
        with mock.patch.object(conn, "host") as host:
            msg = Message(
                subject="testing",
                sender="from@example.com",
                recipients=["to@example.com"],
                body="testing",
            )
            conn.send(msg)

            host.sendmail.assert_called_once_with(
                "from@example.com",
                ["to@example.com"],
                msg.as_bytes(),
                msg.mail_options,
                msg.rcpt_options,
            )


def test_sendmail_with_non_ascii_recipient(mail: Mail) -> None:
    with mail.connect() as conn:
        with mock.patch.object(conn, "host") as host:
            msg = Message(
                subject="testing",
                sender="from@example.com",
                recipients=["ÄÜÖ → ✓ <to@example.com>"],
                body="testing",
            )
            conn.send(msg)

            host.sendmail.assert_called_once_with(
                "from@example.com",
                ["=?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <to@example.com>"],
                msg.as_bytes(),
                msg.mail_options,
                msg.rcpt_options,
            )


def test_sendmail_with_ascii_body(mail: Mail) -> None:
    with mail.connect() as conn:
        with mock.patch.object(conn, "host") as host:
            msg = Message(
                subject="testing",
                sender="from@example.com",
                recipients=["to@example.com"],
                body="body",
            )
            conn.send(msg)

            host.sendmail.assert_called_once_with(
                "from@example.com",
                ["to@example.com"],
                msg.as_bytes(),
                msg.mail_options,
                msg.rcpt_options,
            )


def test_sendmail_with_non_ascii_body(mail: Mail) -> None:
    with mail.connect() as conn:
        with mock.patch.object(conn, "host") as host:
            msg = Message(
                subject="testing",
                sender="from@example.com",
                recipients=["to@example.com"],
                body="Öö",
            )

            conn.send(msg)

            host.sendmail.assert_called_once_with(
                "from@example.com",
                ["to@example.com"],
                msg.as_bytes(),
                msg.mail_options,
                msg.rcpt_options,
            )
