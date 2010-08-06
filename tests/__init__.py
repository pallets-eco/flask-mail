# -*- coding: utf-8 -*-

from __future__ import with_statement

import unittest
import mailbox

from email import encoders

from flask import Flask, g
from flaskext.mail import encoding
from flaskext.mail import Mail, Message, BadHeaderError, Attachment

from nose.tools import assert_equal

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
        
    def test_encoded(self):
        
        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        encoded = msg.encoded()

    def test_to_base(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        base = msg.to_base()

        assert base.headers['Subject'] == "testing"
        assert base.headers['To'] == ['to@example.com']
        assert base.headers['From'] == 'support@mysite.com'
        
        assert base.body == "testing"
        assert base.content_encoding['Content-Type'][0] == 'text/plain'

    def test_to_base_html(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing",
                      html="<b>testing</b>")

        base = msg.to_base()

        assert base.headers['Subject'] == "testing"
        assert base.headers['To'] == ['to@example.com']
        assert base.headers['From'] == 'support@mysite.com'
        
        assert base.body is None
        assert base.content_encoding['Content-Type'][0] == 'multipart/alternative'

    def test_attach(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")
        
        msg.attach(data="this is a test", 
                   content_type="text/plain")
        

        a = msg.attachments[0]
        
        assert a.filename is None
        assert a.disposition == 'attachment'
        assert a.content_type == "text/plain"
        assert a.data == "this is a test"
 
        part = a.encoded(msg.to_base())

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

    def test_max_emails(self):
        
        messages = []

        with self.mail.record_messages() as outbox:
            with self.mail.connect(max_emails=10) as conn:
                for i in xrange(100):
                    msg = Message(subject="testing",
                                  recipients=["to@example.com"],
                                  body="testing")
        
                    conn.send(msg)

                    print conn.num_emails
                    if i % 10 == 0:
                        assert conn.num_emails == 1

            assert len(outbox) == 100

class TestEncoding(TestCase):

    def test_mailbase(self):

        the_subject = u'p\xf6stal'
        m = encoding.MailBase()
        
        m['To'] = "testing@localhost"
        m['Subject'] = the_subject

        assert m['To'] == "testing@localhost"
        assert m['TO'] == m['To']
        assert m['to'] == m['To']

        assert m['Subject'] == the_subject
        assert m['subject'] == m['Subject']
        assert m['sUbjeCt'] == m['Subject']
        
        msg = m.to_message()
        
        for k in m.keys():
            assert k in m
            del m[k]
            assert not k in m

    def test_MIMEPart(self):
        text1 = encoding.MIMEPart("text/plain")
        text1.set_payload("The first payload.")
        text2 = encoding.MIMEPart("text/plain")
        text2.set_payload("The second payload.")

        image_data = open("tests/lamson.png").read()
        img1 = encoding.MIMEPart("image/png")
        img1.set_payload(image_data)
        img1.set_param('attachment','', header='Content-Disposition')
        img1.set_param('filename','lamson.png', header='Content-Disposition')
        encoders.encode_base64(img1)
        
        multi = encoding.MIMEPart("multipart/mixed")
        for x in [text1, text2, img1]:
            multi.attach(x)

    def test_attach_text(self):
        mail = encoding.MailBase()
        mail.attach_text("This is some text.", 'text/plain')

        msg = mail.to_message()
        assert msg.get_payload(0).get_payload() == "This is some text."

        mail.attach_text("<html><body><p>Hi there.</p></body></html>", "text/html")
        msg = mail.to_message()
        assert len(msg.get_payload()) == 2


    def test_attach_file(self):
        mail = encoding.MailBase()
        png = open("tests/lamson.png").read()
        mail.attach_file("lamson.png", png, "image/png", "attachment")
        msg = mail.to_message()

        payload = msg.get_payload(0)
        assert payload.get_payload(decode=True) == png
        assert payload.get_filename() == "lamson.png", payload.get_filename()

    
