import pytest
from flask import Flask

from flask_mail import Mail

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
        "MAIL_DEFAULT_SENDER": "support@example.com",
    })
    
    with app.test_request_context():
        yield app

@pytest.fixture
def mail(app):
    return Mail(app)
