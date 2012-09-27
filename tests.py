# -*- coding: utf-8 -*-

from __future__ import with_statement

import email.utils
import unittest
import time
import re

from flask import Flask
from flask_mail import Mail, Message, BadHeaderError


class TestCase(unittest.TestCase):

    TESTING = True
    DEFAULT_MAIL_SENDER = "support@mysite.com"

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)

        self.assertTrue(self.app.testing)

        self.mail = Mail(self.app)

        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):

        self.ctx.pop()


class TestMessage(TestCase):

    def test_initialize(self):

        msg = Message(subject="subject",
                      recipients=["to@example.com"])

        self.assertEqual(msg.sender, "support@mysite.com")
        self.assertEqual(msg.recipients, ["to@example.com"])

    def test_recipients_properly_initialized(self):

        msg = Message(subject="subject")
        self.assertEqual(msg.recipients, [])

        msg2 = Message(subject="subject")
        msg2.add_recipient("somebody@here.com")
        self.assertEqual(len(msg2.recipients), 1)

    def test_sendto_properly_set(self):
        msg = Message(subject="subject", recipients=["somebody@here.com"],
                       cc=["cc@example.com"], bcc=["bcc@example.com"])
        self.assertEqual(len(msg.send_to), 3)
        msg.add_recipient("cc@example.com")
        self.assertEqual(len(msg.send_to), 3)

    def test_add_recipient(self):

        msg = Message("testing")
        msg.add_recipient("to@example.com")

        self.assertEqual(msg.recipients, ["to@example.com"])

    def test_sender_as_tuple(self):
        msg = Message(subject="testing",
                      sender=("tester", "tester@example.com"))
        self.assertEqual('tester <tester@example.com>', msg.sender)

    def test_reply_to(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      sender="spammer <spammer@example.com>",
                      reply_to="somebody <somebody@example.com>",
                      body="testing")

        response = msg.as_string()
        self.assertIn("Reply-To: somebody <somebody@example.com>", str(response))

    def test_send_without_sender(self):

        del self.app.config['DEFAULT_MAIL_SENDER']

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        self.assertRaises(AssertionError, self.mail.send, msg)

    def test_send_without_recipients(self):

        msg = Message(subject="testing",
                      recipients=[],
                      body="testing")

        self.assertRaises(AssertionError, self.mail.send, msg)

    def test_send_without_body(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"])

        self.assertRaises(AssertionError, self.mail.send, msg)

        msg.html = "<b>test</b>"

        self.mail.send(msg)

    def test_normal_send(self):
        """
        This will not actually send a message unless the mail server
        is set up. The error will be logged but test should still
        pass.
        """

        self.app.config['TESTING'] = False
        self.mail.init_app(self.app)

        with self.mail.record_messages() as outbox:

            msg = Message(subject="testing",
                          recipients=["to@example.com"],
                          body="testing")

            self.mail.send(msg)

            self.assertEqual(len(outbox), 1)

        self.app.config['TESTING'] = True

    def test_bcc(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing",
                      bcc=["tosomeoneelse@example.com"])

        response = msg.as_string()
        self.assertIn("Bcc: tosomeoneelse@example.com", str(response))

    def test_cc(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing",
                      cc=["tosomeoneelse@example.com"])

        response = msg.as_string()
        self.assertIn("Cc: tosomeoneelse@example.com", str(response))

    def test_attach(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        msg.attach(data="this is a test",
                   content_type="text/plain")

        a = msg.attachments[0]

        self.assertIsNone(a.filename)
        self.assertEqual(a.disposition, 'attachment')
        self.assertEqual(a.content_type, "text/plain")
        self.assertEqual(a.data, "this is a test")

    def test_bad_header_subject(self):

        msg = Message(subject="testing\n\r",
                      sender="from@example.com",
                      body="testing",
                      recipients=["to@example.com"])

        self.assertRaises(BadHeaderError, self.mail.send, msg)

    def test_bad_header_sender(self):

        msg = Message(subject="testing",
                      sender="from@example.com\n\r",
                      recipients=["to@example.com"],
                      body="testing")

        self.assertRaises(BadHeaderError, self.mail.send, msg)

    def test_bad_header_reply_to(self):

        msg = Message(subject="testing",
                      sender="from@example.com",
                      reply_to="evil@example.com\n\r",
                      recipients=["to@example.com"],
                      body="testing")

        self.assertRaises(BadHeaderError, self.mail.send, msg)

    def test_bad_header_recipient(self):

        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=[
                          "to@example.com",
                          "to\r\n@example.com"],
                      body="testing")

        self.assertRaises(BadHeaderError, self.mail.send, msg)

    def test_plain_message(self):

        plain_text = "Hello Joe,\nHow are you?"

        msg = Message(subject="subject",
                      recipients=["to@example.com"],
                      body=plain_text)

        self.assertEqual(plain_text, msg.body)
        self.assertIn('Content-Type: text/plain', msg.as_string())

    def test_message_str(self):
        msg = Message(subject="subject",
                      recipients=["to@example.com"],
                      body="some plain text")
        self.assertEqual(msg.as_string(), str(msg))

    def test_plain_message_with_attachments(self):
        msg = Message(subject="subject",
                      recipients=["to@example.com"],
                      body="hello")

        msg.attach(data="this is a test",
                   content_type="text/plain")

        self.assertIn('Content-Type: multipart/mixed', msg.as_string())

    def test_html_message(self):
        html_text = "<p>Hello World</p>"

        msg = Message(subject="subject",
                      recipients=["to@example.com"],
                      html=html_text)

        self.assertEqual(html_text, msg.html)
        self.assertIn('Content-Type: multipart/alternative', msg.as_string())

    def test_date_header(self):
        before = time.time()

        msg = Message(subject="subject",
                      recipients=["to@example.com"],
                      body="hello",
                      date=time.time())

        after = time.time()
        self.assertTrue(before <= msg.date <= after)

        dateFormatted = email.utils.formatdate(msg.date, localtime=True)
        self.assertIn('Date: ' + dateFormatted, msg.as_string())

    def test_msgid_header(self):
        msg = Message(subject="subject",
                      recipients=["to@example.com"],
                      body="hello")

        # see RFC 5322 section 3.6.4. for the exact format specification
        r = re.compile(r"<\S+@\S+>").match(msg.msgId)
        self.assertIsNotNone(r)
        self.assertIn('Message-ID: ' + msg.msgId, msg.as_string())

    def test_unicode_sender(self):
        msg = Message(subject="subject",
                sender=(u"ÄÜÖ → ✓", 'from@example.com>'),
                recipients=["to@example.com"])

        self.assertIn('From: =?utf-8?b?w4TDnMOWIOKGkiDinJMgPGZyb21AZXhhbXBsZS5jb20+Pg==?=', msg.as_string())

    def test_extra_headers(self):
        msg = Message(subject="subject",
                      recipients=["to@example.com"],
                      body="hello",
                      extra_headers={'X-Extra-Header': 'Yes'})

        self.assertIn('X-Extra-Header: Yes', msg.as_string())

    def test_message_charset(self):
        msg = Message(subject="subject",
                recipients=["foo@bar.com"],
                charset='us-ascii')

        # ascii body
        msg.body = "normal ascii text"
        self.assertIn('Content-Type: text/plain; charset="us-ascii"', msg.as_string())

        # ascii html
        msg = Message(subject="subject",
                recipients=["foo@bar.com"],
                charset='us-ascii')
        msg.body = None
        msg.html = "<html><h1>hello</h1></html>"
        self.assertIn('Content-Type: text/html; charset="us-ascii"', msg.as_string())

        # unicode body
        msg = Message(subject="subject",
                recipients=["foo@bar.com"])
        msg.body = u"ünicöde ←→ ✓"
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())

        # unicode body and unicode html
        msg = Message(subject="subject",
                recipients=["foo@bar.com"])
        msg.html = u"ünicöde ←→ ✓"
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())
        self.assertIn('Content-Type: text/html; charset="utf-8"', msg.as_string())

        # unicode body and attachments
        msg = Message(subject="subject",
                recipients=["foo@bar.com"])
        msg.html = None
        msg.attach(data="foobar", content_type='text/csv')
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())


class TestMail(TestCase):

    def test_send(self):

        with self.mail.record_messages() as outbox:
            msg = Message(subject="testing",
                          recipients=["tester@example.com"],
                          body="test")

            self.mail.send(msg)
            self.assertIsNotNone(msg.date)

            self.assertEqual(len(outbox), 1)

    def test_send_message(self):

        with self.mail.record_messages() as outbox:
            self.mail.send_message(subject="testing",
                                   recipients=["tester@example.com"],
                                   body="test")

            self.assertEqual(len(outbox), 1)

            msg = outbox[0]

            self.assertEqual(msg.subject, "testing")
            self.assertEqual(msg.recipients, ["tester@example.com"])
            self.assertEqual(msg.body, "test")


class TestConnection(TestCase):

    def test_send_message(self):

        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                conn.send_message(subject="testing",
                                  recipients=["to@example.com"],
                                  body="testing")

            self.assertEqual(len(outbox), 1)

    def test_send_single(self):

        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                msg = Message(subject="testing",
                              recipients=["to@example.com"],
                              body="testing")

                conn.send(msg)

            self.assertEqual(len(outbox), 1)

    def test_send_many(self):

        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                for i in xrange(100):
                    msg = Message(subject="testing",
                                  recipients=["to@example.com"],
                                  body="testing")

                    conn.send(msg)

            self.assertEqual(len(outbox), 100)

    def test_max_emails(self):

        with self.mail.record_messages() as outbox:
            with self.mail.connect(max_emails=10) as conn:
                for i in xrange(100):
                    msg = Message(subject="testing",
                                  recipients=["to@example.com"],
                                  body="testing")

                    conn.send(msg)

                    if i % 10 == 0:
                        self.assertEqual(conn.num_emails, 1)

            self.assertEqual(len(outbox), 100)
