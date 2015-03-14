#!/usr/bin/env python2.7

from google.appengine.api import users

from flask import Flask
from flask.ext.mail import Mail, Message


class Config(object):
    MAIL_USE_APPENGINE = True


app = Flask(__name__)
app.config.from_object(Config())

mail = Mail(app)


@app.route('/')
def home():
    me = users.get_current_user()
    message = Message(
        'Hi there',
        recipients=[me.email()],
        sender=me.email(),
        body='This is my email body')
    mail.send(message)
    return 'I sent you an email!'
