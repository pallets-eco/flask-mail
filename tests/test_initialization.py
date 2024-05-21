def test_init_mail(flask_mail):
    app, app_mail = flask_mail

    mail = app_mail.init_mail(app.config, app.debug, app.testing)
    assert app_mail.state.__dict__ == mail.__dict__
