# Flask-Mail

Flask-Mail is an extension for Flask that makes it easy to send emails from your Flask application. It simplifies the process of integrating email functionality, allowing you to focus on building great features for your application.

## Installation

You can install Flask-Mail using pip:

```bash
pip install Flask-Mail
```

## Usage

To use Flask-Mail in your Flask application, you need to import and configure it. Here's a simple example:
```python
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'your_mail_server'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_username'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

mail = Mail(app)

@app.route('/')
def send_email():
  msg = Message(
    'Hello',
    recipients=['recipient@example.com'],
    body='This is a test email sent from Flask-Mail!'
  )
  mail.send(msg)
  return 'Email sent succesfully!'
```
Make sure to replace placeholder values in the configuration with your actual email server details.

## Documentation

For more detailed information and advanced usage, please refer to the official [Flask-Mail documentation](https://pythonhosted.org/Flask-Mail/).

## Contributing

If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/mattupstate/flask-mail).
