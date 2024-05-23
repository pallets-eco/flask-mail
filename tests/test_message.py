from __future__ import annotations

import base64
import email.message
import email.utils
import re
import time
from email.header import Header

import pytest
from flask import Flask

from flask_mail import BadHeaderError
from flask_mail import Mail
from flask_mail import Message
from flask_mail import sanitize_address


def test_init_message(app: Flask, mail: Mail) -> None:
    msg = Message(subject="subject", recipients=["to@example.com"])
    assert msg.sender == app.extensions["mail"].default_sender
    assert msg.recipients == ["to@example.com"]


def test_init_message_recipients(app: Flask, mail: Mail) -> None:
    msg = Message(subject="subject")
    assert msg.recipients == []

    msg2 = Message(subject="subject")
    msg2.add_recipient("somebody@here.com")
    assert len(msg2.recipients) == 1


def test_esmtp_options_properly_initialized(app: Flask, mail: Mail) -> None:
    msg = Message(subject="subject")
    assert msg.mail_options == []
    assert msg.rcpt_options == []

    msg = Message(subject="subject", mail_options=["BODY=8BITMIME"])
    assert msg.mail_options == ["BODY=8BITMIME"]

    msg2 = Message(subject="subject", rcpt_options=["NOTIFY=SUCCESS"])
    assert msg2.rcpt_options == ["NOTIFY=SUCCESS"]


def test_sendto_properly_set(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="subject",
        recipients=["somebody@here.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
    )
    assert len(msg.send_to) == 3
    msg.add_recipient("cc@example.com")
    assert len(msg.send_to) == 3


def test_add_recipient(app: Flask, mail: Mail) -> None:
    msg = Message("testing")
    msg.add_recipient("to@example.com")
    assert msg.recipients == ["to@example.com"]


def test_sender_as_tuple(app: Flask, mail: Mail) -> None:
    msg = Message(subject="testing", sender=("tester", "tester@example.com"))
    assert "tester <tester@example.com>" == msg.sender


def test_default_sender_as_tuple(app: Flask, mail: Mail) -> None:
    app.extensions["mail"].default_sender = ("tester", "tester@example.com")
    msg = Message(subject="testing")
    assert "tester <tester@example.com>" == msg.sender


def test_reply_to(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="testing",
        recipients=["to@example.com"],
        sender="spammer <spammer@example.com>",
        reply_to="somebody <somebody@example.com>",
        body="testing",
    )
    response = msg.as_string()

    h = Header(
        "Reply-To: {}".format(sanitize_address("somebody <somebody@example.com>"))
    )
    assert h.encode() in str(response)


def test_send_without_sender(app: Flask, mail: Mail) -> None:
    app.extensions["mail"].default_sender = None
    msg = Message(subject="testing", recipients=["to@example.com"], body="testing")
    with pytest.raises(AssertionError):
        mail.send(msg)


def test_send_without_recipients(app: Flask, mail: Mail) -> None:
    app.extensions["mail"].default_sender = None
    msg = Message(subject="testing", recipients=[], body="testing")
    with pytest.raises(AssertionError):
        mail.send(msg)


def test_bcc(app: Flask, mail: Mail) -> None:
    msg = Message(
        sender="from@example.com",
        subject="testing",
        recipients=["to@example.com"],
        body="testing",
        bcc=["tosomeoneelse@example.com"],
    )
    response = msg.as_string()
    assert "tosomeoneelse@example.com" not in str(response)


def test_cc(app: Flask, mail: Mail) -> None:
    msg = Message(
        sender="from@example.com",
        subject="testing",
        recipients=["to@example.com"],
        body="testing",
        cc=["tosomeoneelse@example.com"],
    )
    response = msg.as_string()
    assert "Cc: tosomeoneelse@example.com" in str(response)


def test_attach(app: Flask, mail: Mail) -> None:
    msg = Message(subject="testing", recipients=["to@example.com"], body="testing")
    msg.attach(data=b"this is a test", content_type="text/plain")
    a = msg.attachments[0]
    assert a.filename is None
    assert a.disposition == "attachment"
    assert a.content_type == "text/plain"
    assert a.data == b"this is a test"


def test_bad_header_subject(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="testing\r\n",
        sender="from@example.com",
        body="testing",
        recipients=["to@example.com"],
    )
    with pytest.raises(BadHeaderError):
        mail.send(msg)


def test_multiline_subject(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="testing\r\n testing\r\n testing \r\n \ttesting",
        sender="from@example.com",
        body="testing",
        recipients=["to@example.com"],
    )
    mail.send(msg)
    response = msg.as_string()
    assert "From: from@example.com" in str(response)
    assert "testing\r\n testing\r\n testing \r\n \ttesting" in str(response)


def test_bad_multiline_subject(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="testing\r\n testing\r\n ",
        sender="from@example.com",
        body="testing",
        recipients=["to@example.com"],
    )
    with pytest.raises(BadHeaderError):
        mail.send(msg)

    msg = Message(
        subject="testing\r\n testing\r\n\t",
        sender="from@example.com",
        body="testing",
        recipients=["to@example.com"],
    )
    with pytest.raises(BadHeaderError):
        mail.send(msg)

    msg = Message(
        subject="testing\r\n testing\r\n\n",
        sender="from@example.com",
        body="testing",
        recipients=["to@example.com"],
    )
    with pytest.raises(BadHeaderError):
        mail.send(msg)


def test_bad_header_sender(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="testing",
        sender="from@example.com\r\n",
        recipients=["to@example.com"],
        body="testing",
    )

    assert "From: from@example.com" in msg.as_string()


def test_bad_header_reply_to(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="testing",
        sender="from@example.com",
        reply_to="evil@example.com\r",
        recipients=["to@example.com"],
        body="testing",
    )

    assert "From: from@example.com" in msg.as_string()
    assert "To: to@example.com" in msg.as_string()
    assert "Reply-To: evil@example.com" in msg.as_string()


def test_bad_header_recipient(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="testing",
        sender="from@example.com",
        recipients=["to@example.com", "to\r\n@example.com"],
        body="testing",
    )

    assert "To: to@example.com" in msg.as_string()


def test_emails_are_sanitized(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="testing",
        sender="sender\r\n@example.com",
        reply_to="reply_to\r\n@example.com",
        recipients=["recipient\r\n@example.com"],
    )
    assert "sender@example.com" in msg.as_string()
    assert "reply_to@example.com" in msg.as_string()
    assert "recipient@example.com" in msg.as_string()


def test_plain_message(app: Flask, mail: Mail) -> None:
    plain_text = "Hello Joe,\nHow are you?"
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        body=plain_text,
    )
    assert plain_text == msg.body
    assert "Content-Type: text/plain" in msg.as_string()


def test_message_str(app: Flask, mail: Mail) -> None:
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        body="some plain text",
    )
    assert msg.as_string() == str(msg)


def test_plain_message_with_attachments(app: Flask, mail: Mail) -> None:
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        body="hello",
    )

    msg.attach(data=b"this is a test", content_type="text/plain")

    assert "Content-Type: multipart/mixed" in msg.as_string()


def test_plain_message_with_ascii_attachment(app: Flask, mail: Mail) -> None:
    msg = Message(subject="subject", recipients=["to@example.com"], body="hello")

    msg.attach(
        data=b"this is a test", content_type="text/plain", filename="test doc.txt"
    )

    assert 'Content-Disposition: attachment; filename="test doc.txt"' in msg.as_string()


def test_plain_message_with_unicode_attachment(app: Flask, mail: Mail) -> None:
    msg = Message(subject="subject", recipients=["to@example.com"], body="hello")

    msg.attach(
        data=b"this is a test",
        content_type="text/plain",
        filename="ünicöde ←→ ✓.txt",
    )

    parsed = email.message_from_string(msg.as_string())
    payload = parsed.get_payload(1)
    assert isinstance(payload, email.message.Message)
    disposition = payload.get("Content-Disposition")
    assert disposition is not None
    disposition = re.sub(r"\s+", " ", disposition)

    assert disposition in [
        "attachment; filename*=\"UTF8''%C3%BCnic%C3%B6de%20%E2%86%90%E2%86%92%20%E2%9C%93.txt\"",  # noqa: E501
        "attachment; filename*=UTF8''%C3%BCnic%C3%B6de%20%E2%86%90%E2%86%92%20%E2%9C%93.txt",  # noqa: E501
    ]


def test_plain_message_with_ascii_converted_attachment(app: Flask, mail: Mail) -> None:
    mail.state.ascii_attachments = True  # type: ignore[union-attr]
    msg = Message(subject="subject", recipients=["to@example.com"], body="hello")

    msg.attach(
        data=b"this is a test",
        content_type="text/plain",
        filename="ünicödeß ←.→ ✓.txt",
    )

    assert (
        'Content-Disposition: attachment; filename="unicode . .txt"' in msg.as_string()
    )


def test_html_message(app: Flask, mail: Mail) -> None:
    html_text = "<p>Hello World</p>"
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        html=html_text,
    )

    assert html_text == msg.html
    assert "Content-Type: multipart/alternative" in msg.as_string()


def test_json_message(app: Flask, mail: Mail) -> None:
    json_text = '{"msg": "Hello World!}'
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        alts={"json": json_text},
    )

    assert json_text == msg.alts["json"]
    assert "Content-Type: multipart/alternative" in msg.as_string()


def test_html_message_with_attachments(app: Flask, mail: Mail) -> None:
    html_text = "<p>Hello World</p>"
    plain_text = "Hello World"
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        body=plain_text,
        html=html_text,
    )
    msg.attach(data=b"this is a test", content_type="text/plain")

    assert html_text == msg.html
    assert "Content-Type: multipart/alternative" in msg.as_string()

    parsed = email.message_from_string(msg.as_string())
    assert len(parsed.get_payload()) == 2

    payload = parsed.get_payload()
    assert isinstance(payload, list)
    body, attachment = payload
    assert isinstance(body, email.message.Message)
    assert isinstance(attachment, email.message.Message)
    assert len(body.get_payload()) == 2

    payload = body.get_payload()
    assert isinstance(payload, list)
    plain, html = payload
    assert isinstance(plain, email.message.Message)
    assert isinstance(html, email.message.Message)
    assert plain.get_payload() == plain_text
    assert html.get_payload() == html_text
    payload = attachment.get_payload()
    assert isinstance(payload, str)
    assert base64.b64decode(payload) == b"this is a test"


def test_date_header(app: Flask, mail: Mail) -> None:
    before = time.time()
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        body="hello",
        date=time.time(),
    )
    after = time.time()

    assert msg.date is not None
    assert before <= msg.date <= after
    formatted = email.utils.formatdate(msg.date, localtime=True)
    assert "Date: " + formatted in msg.as_string()


def test_msgid_header(app: Flask, mail: Mail) -> None:
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        body="hello",
    )

    # see RFC 5322 section 3.6.4. for the exact format specification
    r = re.compile(r"<\S+@\S+>").match(msg.msgId)
    assert r is not None
    assert "Message-ID: " + msg.msgId in msg.as_string()


def test_unicode_sender_tuple(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="subject",
        sender=("ÄÜÖ → ✓", "from@example.com>"),
        recipients=["to@example.com"],
    )

    assert (
        "From: =?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <from@example.com>" in msg.as_string()
    )


def test_unicode_sender(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="subject",
        sender="ÄÜÖ → ✓ <from@example.com>>",
        recipients=["to@example.com"],
    )

    assert (
        "From: =?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <from@example.com>" in msg.as_string()
    )


def test_unicode_headers(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="subject",
        sender="ÄÜÖ → ✓ <from@example.com>",
        recipients=["Ä <t1@example.com>", "Ü <t2@example.com>"],
        cc=["Ö <cc@example.com>"],
    )

    response = msg.as_string()
    a1 = sanitize_address("Ä <t1@example.com>")
    a2 = sanitize_address("Ü <t2@example.com>")
    h1_a = Header(f"To: {a1}, {a2}")
    h1_b = Header(f"To: {a2}, {a1}")
    h2 = Header("From: {}".format(sanitize_address("ÄÜÖ → ✓ <from@example.com>")))
    h3 = Header("Cc: {}".format(sanitize_address("Ö <cc@example.com>")))

    # Ugly, but there's no guaranteed order of the recipients in the header
    try:
        assert h1_a.encode() in response
    except AssertionError:
        assert h1_b.encode() in response

    assert h2.encode() in response
    assert h3.encode() in response


def test_unicode_subject(app: Flask, mail: Mail) -> None:
    msg = Message(
        subject="sübject",
        sender="from@example.com",
        recipients=["to@example.com"],
    )
    assert "=?utf-8?q?s=C3=BCbject?=" in msg.as_string()


def test_extra_headers(app: Flask, mail: Mail) -> None:
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["to@example.com"],
        body="hello",
        extra_headers={"X-Extra-Header": "Yes"},
    )
    assert "X-Extra-Header: Yes" in msg.as_string()


def test_message_charset(app: Flask, mail: Mail) -> None:
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["foo@bar.com"],
        charset="us-ascii",
    )

    # ascii body
    msg.body = "normal ascii text"
    assert 'Content-Type: text/plain; charset="us-ascii"' in msg.as_string()

    # ascii html
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["foo@bar.com"],
        charset="us-ascii",
    )
    msg.body = None
    msg.html = "<html><h1>hello</h1></html>"
    assert 'Content-Type: text/html; charset="us-ascii"' in msg.as_string()

    # unicode body
    msg = Message(
        sender="from@example.com", subject="subject", recipients=["foo@bar.com"]
    )
    msg.body = "ünicöde ←→ ✓"
    assert 'Content-Type: text/plain; charset="utf-8"' in msg.as_string()

    # unicode body and unicode html
    msg = Message(
        sender="from@example.com", subject="subject", recipients=["foo@bar.com"]
    )
    msg.html = "ünicöde ←→ ✓"
    assert 'Content-Type: text/plain; charset="utf-8"' in msg.as_string()
    assert 'Content-Type: text/html; charset="utf-8"' in msg.as_string()

    # unicode body and attachments
    msg = Message(
        sender="from@example.com", subject="subject", recipients=["foo@bar.com"]
    )
    msg.html = None
    msg.attach(data=b"foobar", content_type="text/csv")
    assert 'Content-Type: text/plain; charset="utf-8"' in msg.as_string()

    # unicode sender as tuple
    msg = Message(
        sender=("送信者", "from@example.com"),
        subject="表題",
        recipients=["foo@bar.com"],
        reply_to="返信先 <somebody@example.com>",
        charset="shift_jis",
    )  # japanese
    msg.body = "内容"
    assert "From: =?iso-2022-jp?" in msg.as_string()
    assert "From: =?utf-8?" not in msg.as_string()
    assert "Subject: =?iso-2022-jp?" in msg.as_string()
    assert "Subject: =?utf-8?" not in msg.as_string()
    assert "Reply-To: =?iso-2022-jp?" in msg.as_string()
    assert "Reply-To: =?utf-8?" not in msg.as_string()
    assert 'Content-Type: text/plain; charset="iso-2022-jp"' in msg.as_string()

    # unicode subject sjis
    msg = Message(
        sender="from@example.com",
        subject="表題",
        recipients=["foo@bar.com"],
        charset="shift_jis",
    )  # japanese
    msg.body = "内容"
    assert "Subject: =?iso-2022-jp?" in msg.as_string()
    assert 'Content-Type: text/plain; charset="iso-2022-jp"' in msg.as_string()

    # unicode subject utf-8
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["foo@bar.com"],
        charset="utf-8",
    )
    msg.body = "内容"
    assert "Subject: subject" in msg.as_string()
    assert 'Content-Type: text/plain; charset="utf-8"' in msg.as_string()

    # ascii subject
    msg = Message(
        sender="from@example.com",
        subject="subject",
        recipients=["foo@bar.com"],
        charset="us-ascii",
    )
    msg.body = "normal ascii text"
    assert "Subject: =?us-ascii?" not in msg.as_string()
    assert 'Content-Type: text/plain; charset="us-ascii"' in msg.as_string()

    # default charset
    msg = Message(
        sender="from@example.com", subject="subject", recipients=["foo@bar.com"]
    )
    msg.body = "normal ascii text"
    assert "Subject: =?" not in msg.as_string()
    assert 'Content-Type: text/plain; charset="utf-8"' in msg.as_string()


def test_empty_subject_header(app: Flask, mail: Mail) -> None:
    msg = Message(sender="from@example.com", recipients=["foo@bar.com"])
    msg.body = "normal ascii text"
    mail.send(msg)
    assert "Subject:" not in msg.as_string()
