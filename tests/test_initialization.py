from __future__ import annotations

from flask import Flask

from flask_mail import Mail


def test_init_mail(app: Flask, mail: Mail) -> None:
    new_mail = mail.init_mail(app.config, app.debug, app.testing)
    assert mail.state.__dict__ == new_mail.__dict__
