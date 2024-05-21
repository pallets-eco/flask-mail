from flask_mail import Message


def test_send(app, mail):
    with mail.record_messages() as outbox:
        msg = Message(subject="testing", recipients=["tester@example.com"], body="test")
        mail.send(msg)
        assert msg.date is not None
        assert len(outbox) == 1
        assert msg.sender == app.extensions["mail"].default_sender


def test_send_message(app, mail):
    with mail.record_messages() as outbox:
        mail.send_message(
            subject="testing", recipients=["tester@example.com"], body="test"
        )
        assert len(outbox) == 1
        msg = outbox[0]
        assert msg.subject == "testing"
        assert msg.recipients == ["tester@example.com"]
        assert msg.body == "test"
        assert msg.sender == app.extensions["mail"].default_sender
