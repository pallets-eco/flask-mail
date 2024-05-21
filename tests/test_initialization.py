def test_init_mail(app, mail):
    new_mail = mail.init_mail(app.config, app.debug, app.testing)
    assert mail.state.__dict__ == new_mail.__dict__
