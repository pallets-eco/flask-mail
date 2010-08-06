"""
Encoding functionality.

This code has been adapted from the Lamson encoding module.
"""
import string

from email import encoders
from email.charset import Charset
from email.mime.base import MIMEBase
from email.utils import parseaddr

DEFAULT_ENCODING = "utf-8"
ADDRESS_HEADERS_WHITELIST = ['From', 'To', 'Delivered-To', 'Cc', 'Bcc']
VALUE_IS_EMAIL_ADDRESS = lambda v: '@' in v

class EncodingError(Exception): 
    """Thrown when there is an encoding error."""
    pass


def normalize_header(header):
    return string.capwords(header.lower(), '-')


def header_to_mime_encoding(value, not_email=False):
    if not value: return ""

    encoder = Charset(DEFAULT_ENCODING)
    if type(value) == list:
        return "; ".join(properly_encode_header(
            v, encoder, not_email) for v in value)
    else:
        return properly_encode_header(value, encoder, not_email)


def properly_encode_header(value, encoder, not_email):
    """
    The only thing special (weird) about this function is that it tries
    to do a fast check to see if the header value has an email address in
    it.  Since random headers could have an email address, and email addresses
    have weird special formatting rules, we have to check for it.

    Normally this works fine, but in Librelist, we need to "obfuscate" email
    addresses by changing the '@' to '-AT-'.  This is where
    VALUE_IS_EMAIL_ADDRESS exists.  It's a simple lambda returning True/False
    to check if a header value has an email address.  If you need to make this
    check different, then change this.
    """
    try:
        return value.encode("ascii")
    except UnicodeEncodeError:
        if not_email is False and VALUE_IS_EMAIL_ADDRESS(value):
            # this could have an email address, make sure we don't screw it up
            name, address = parseaddr(value)
            return '"%s" <%s>' % (encoder.header_encode(name.encode("utf-8")), address)

        return encoder.header_encode(value.encode("utf-8"))


class MIMEPart(MIMEBase):
    """
    A reimplementation of nearly everything in email.mime to be more useful
    for actually attaching things.  Rather than one class for every type of
    thing you'd encode, there's just this one, and it figures out how to
    encode what you ask it.
    """
    def __init__(self, type, **params):
        self.maintype, self.subtype = type.split('/')
        MIMEBase.__init__(self, self.maintype, self.subtype, **params)

    def add_text(self, content):
        # this is text, so encode it in canonical form
        try:
            encoded = content.encode('ascii')
            charset = 'ascii'
        except UnicodeError:
            encoded = content.encode('utf-8')
            charset = 'utf-8'

        self.set_payload(encoded, charset=charset)

    def extract_payload(self, mail):
        if mail.body == None: return  # only None, '' is still ok

        ctype, ctype_params = mail.content_encoding['Content-Type']
        cdisp, cdisp_params = mail.content_encoding['Content-Disposition']

        assert ctype, """
            Extract payload requires that 
            mail.content_encoding have a valid Content-Type."""

        if ctype.startswith("text/"):
            self.add_text(mail.body)
        else:
            if cdisp:
                # replicate the content-disposition settings
                self.add_header('Content-Disposition', cdisp, **cdisp_params)

            self.set_payload(mail.body)
            encoders.encode_base64(self)

    def __repr__(self):
        return "<MIMEPart '%s/%s': %r, %r, multipart=%r>" % \
                (self.subtype, 
                 self.maintype, 
                 self['Content-Type'],
                 self['Content-Disposition'],
                 self.is_multipart())


class MailBase(object):
    """MailBase is used as the basis of lamson.mail and contains the basics of
    encoding an email.  You actually can do all your email processing with this
    class, but it's more raw.
    """
    def __init__(self, items=()):
        self.headers = dict(items)
        self.parts = []
        self.body = None
        self.content_encoding = {'Content-Type': (None, {}), 
                                 'Content-Disposition': (None, {}),
                                 'Content-Transfer-Encoding': (None, {})}

    def __getitem__(self, key):
        return self.headers.get(normalize_header(key), None)

    def __len__(self):
        return len(self.headers)

    def __iter__(self):
        return iter(self.headers)

    def __contains__(self, key):
        return normalize_header(key) in self.headers

    def __setitem__(self, key, value):
        self.headers[normalize_header(key)] = value

    def __delitem__(self, key):
        del self.headers[normalize_header(key)]

    def __nonzero__(self):
        return self.body != None or len(self.headers) > 0 or len(self.parts) > 0

    def keys(self):
        """Returns the sorted keys."""
        return sorted(self.headers.keys())

    def attach_file(self, filename, data, ctype, disposition):
        """
        A file attachment is a raw attachment with a disposition that
        indicates the file name.
        """
        assert filename, "You can't attach a file without a filename."
        assert ctype.lower() == ctype, "Hey, don't be an ass.  Use a lowercase content type."

        part = MailBase()
        part.body = data
        part.content_encoding['Content-Type'] = (ctype, {'name': filename})
        part.content_encoding['Content-Disposition'] = (disposition,
                                                        {'filename': filename})
        self.parts.append(part)


    def attach_text(self, data, ctype):
        """
        This attaches a simpler text encoded part, which doesn't have a
        filename.
        """
        assert ctype.lower() == ctype, "Hey, don't be an ass.  Use a lowercase content type."

        part = MailBase()
        part.body = data
        part.content_encoding['Content-Type'] = (ctype, {})
        self.parts.append(part)

    def to_message(self):
        """
        This will construct a MIMEPart that is canonicalized for 
        use with the Python email API.
        """
        ctype, params = self.content_encoding['Content-Type']

        if not ctype:
            if self.parts:
                ctype = 'multipart/mixed'
            else:
                ctype = 'text/plain'
        else:
            if self.parts:
                assert ctype.startswith("multipart") or \
                    ctype.startswith("message"), \
                    "Content type should be multipart or message, not %r" % ctype

        # adjust the content type according to what it should be now
        self.content_encoding['Content-Type'] = (ctype, params)

        try:
            out = MIMEPart(ctype, **params)
        except TypeError, exc:
            raise EncodingError("Content-Type malformed, not allowed: %r; "
                                "%r (Python ERROR: %s" % (ctype, params, exc.message))

        for k in self.keys():
            if k in ADDRESS_HEADERS_WHITELIST:
                out[k.encode('ascii')] = header_to_mime_encoding(self[k])
            else:
                out[k.encode('ascii')] = \
                    header_to_mime_encoding(self[k], not_email=True)

        out.extract_payload(self)

        # go through the children
        for part in self.parts:
            out.attach(part.to_message())

        return out

