import unittest

from flask import Flask, g
from flaskext.mail import init_mail, Message

class TestCase(unittest.TestCase):

    MAIL_TEST_ENV = True
    DEFAULT_MAIL_SENDER = "support@mysite.com"

    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)
        
        init_mail(self.app)

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

        msg = Message(subject="subject")

        assert msg.recipients == []

    def test_add_recipient(self):

        msg = Message("testing")
        msg.add_recipient("to@example.com")

        assert msg.recipients == ["to@example.com"]

    def test_send(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        msg.send()

        assert len(g.outbox) == 1
        assert g.outbox[0].subject == "testing"
        assert g.outbox[0].body == "testing"

    
    def test_send_without_sender(self):

        del self.app.config['DEFAULT_MAIL_SENDER']

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        self.assertRaises(AssertionError, msg.send)

    def test_send_without_recipients(self):

        msg = Message(subject="testing",
                      recipients=[],
                      body="testing")

        self.assertRaises(AssertionError, msg.send)

    def test_send_without_body(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"])

        self.assertRaises(AssertionError, msg.send)

        msg.html = "<b>test</b>"

        msg.send()

    def test_normal_send(self):
        """
        This will not actually send a message unless the mail server
        is set up. The error will be logged but test should still 
        pass.
        """

        self.app.config['MAIL_TEST_ENV'] = False
        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        msg.send()
        
        try:
            assert False, g.outbox
        except AttributeError:
            pass
    
    def test_attach(self):

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")
        
        msg.attach(data="this is a test", 
                   content_type="text/html")
        
        print msg.attachments

        assert msg.attachments[0] == (None, 
                                      "text/html",
                                      "this is a test",
                                      None)
 


