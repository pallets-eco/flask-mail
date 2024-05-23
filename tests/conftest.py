from __future__ import annotations

import collections.abc as c

import pytest
from flask import Flask

from flask_mail import Mail


@pytest.fixture
def app() -> c.Iterator[Flask]:
    app = Flask(__name__)
    app.config.update(
        {
            "TESTING": True,
            "MAIL_DEFAULT_SENDER": "support@example.com",
        }
    )

    with app.test_request_context():
        yield app


@pytest.fixture
def mail(app: Flask) -> Mail:
    return Mail(app)
