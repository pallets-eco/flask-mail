# -*- coding: utf-8 -*-

from __future__ import with_statement

import unittest

from flask import Flask, g
from flaskext.mail import Mail, Message, BadHeaderError, Attachment

class TestCase(unittest.TestCase):

    TESTING = True
    DEFAULT_MAIL_SENDER = "support@mysite.com"

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)
        
        assert self.app.testing

        self.mail = Mail(self.app)

        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):

        self.ctx.pop()

class TestMessage(TestCase):

    def test_initialize(self):

        msg = Message(subject="subject",
                      recipients=["to@example.com"])


        assert msg.sender == "support@mysite.com"
        assert msg.recipients == ["to@example.com"]

    def test_recipients_properly_initialized(self):

        msg = Message(subject="subject")

        assert msg.recipients == []

        msg2 = Message(subject="subject")
        msg2.add_recipient("somebody@here.com")

        assert len(msg.recipients) == 0

        msg3 = Message(subject="subject")
        msg3.add_recipient("somebody@here.com")

        assert len(msg.recipients) == 0


    def test_add_recipient(self):

        msg = Message("testing")
        msg.add_recipient("to@example.com")

        assert msg.recipients == ["to@example.com"]

    
    def test_sender_as_tuple(self):

        msg = Message(subject="testing",
                      sender=("tester", "tester@example.com"))

    
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
            
            assert len(outbox) == 1
        
        self.app.config['TESTING'] = True
        
            
    
    def test_attach(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")
        
        msg.attach(data="this is a test", 
                   content_type="text/plain")
        

        a = msg.attachments[0]
        
        assert a.filename is None
        assert a.disposition is None
        assert a.content_type == "text/plain"
        assert a.data == "this is a test"
 
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

    def test_bad_header_recipient(self):

        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=[
                          "to@example.com",
                          "to\r\n@example.com"],
                      body="testing")

        self.assertRaises(BadHeaderError, self.mail.send, msg)

class TestMail(TestCase):

    def test_send(self):

        with self.mail.record_messages() as outbox:
            msg = Message(subject="testing",
                          recipients=["tester@example.com"],
                          body="test")

            self.mail.send(msg)

            assert len(outbox) == 1 

    def test_send_message(self):

        with self.mail.record_messages() as outbox:
            self.mail.send_message(subject="testing",
                                   recipients=["tester@example.com"],
                                   body="test")

            assert len(outbox) == 1

            msg = outbox[0]

            assert msg.subject == "testing"
            assert msg.recipients == ["tester@example.com"]
            assert msg.body == "test"


class TestConnection(TestCase):

    def test_send_message(self):

        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                conn.send_message(subject="testing",
                                  recipients=["to@example.com"],
                                  body="testing")

            assert len(outbox) == 1

    def test_send_single(self):

        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                msg = Message(subject="testing",
                              recipients=["to@example.com"],
                              body="testing")

                conn.send(msg)

            assert len(outbox) == 1

    def test_send_many(self):
        
        messages = []

        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                for i in xrange(100):
                    msg = Message(subject="testing",
                                  recipients=["to@example.com"],
                                  body="testing")
        
                    conn.send(msg)

            assert len(outbox) == 100
