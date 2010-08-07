
try:
    
    import blinker
    signals = blinker.Namespace()
    
    email_dispatched = signals.signal("email-dispatched", doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
    """)

except ImportError:
    email_dispatched = None

