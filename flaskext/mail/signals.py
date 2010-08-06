
try:
    import blinker
    signals = blinker.Namespace()
    email_dispatched = signals.signal("email-dispatched")
except ImportError:
    email_dispatched = None

