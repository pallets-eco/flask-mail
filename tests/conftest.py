import pytest
from flask import Flask

from flask_mail import Mail

TESTING_FLASK_APP_CONFIG = {
    "TESTING": True,
    "MAIL_DEFAULT_SENDER": "support@mysite.com",
}


@pytest.fixture
def flask_mail(
    scope="module",
):
    app = Flask(__name__)
    app.config.update(**TESTING_FLASK_APP_CONFIG)
    assert app.testing is True
    mail = Mail(app)
    ctx = app.test_request_context()
    ctx.push()
    yield app, mail
    ctx.pop()
