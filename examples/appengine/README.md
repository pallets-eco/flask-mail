# App Engine example

Here's an example app that uses Flask-Mail.

Set up dependencies for the App Engine bundle:

```
pip install -t examples/appengine/lib .
```

If you get an error doing that, it may be because you're on Mac OS X using Homebrew. [Follow these instructions](https://github.com/Homebrew/homebrew/blob/master/share/doc/homebrew/Homebrew-and-Python.md#note-on-pip-install---user) to set up a `.pydistutils.cfg` in your home directory to make this work.

Run the development server locally:

```
dev_appserver.py examples/appengine
```

Visit <http://localhost:8080> to test out the app and send yourself a test email. In local debug mode this will just print logging messages to the console. In production it will send a real email.
