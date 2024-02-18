#!/usr/local/bin/python
from email.parser import Parser as EmailParser
from io import BytesIO
import mimetypes, hashlib

class NotSupportedMailFormat(Exception):
    pass

def get_full_emails(addresses):
    results = []
    for a in addresses:
        if a.name:
            results.append(f"{a.name.decode('utf-8')} <{a.mailbox.decode('utf-8')}@{a.host.decode('utf-8')}>")
        else:
            results.append(f"{a.mailbox.decode('utf-8')}@{a.host.decode('utf-8')}")
    return results

def get_address_only(addresses):
    results = []
    for a in addresses:
        results.append(f"{a.mailbox.decode('utf-8')}@{a.host.decode('utf-8')}")
    return results

def parse_attachment(part):
    content_disposition = part.get('Content-Disposition')
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if content_disposition and dispositions[0].lower() == "attachment":
            name = part.get_filename()
            if not name:
                return None
            data = part.get_payload(decode=True)
            if not data:
                return None
            attachment = Object()
            attachment.data = data
            attachment.ctype = mimetypes.guess_type(name)[0]
            attachment.size = len(data)
            attachment.name = name
            attachment.hash = hashlib.sha1(data).hexdigest()

            return attachment

    return None

def parse(content):
    body = None
    html = None
    attachments = []
    for part in EmailParser().parsestr(content).walk():
        attachment = parse_attachment(part)
        if attachment:
            attachments.append(attachment)
        elif part.get_content_type() == "text/plain":
            if body is None:
                body = bytes()
            body += part.get_payload(decode=True)
        elif part.get_content_type() == "text/html":
            if html is None:
                html = bytes()
            html += part.get_payload(decode=True)

    return {
        'body' : body,
        'html' : html,
        'attachments': attachments,
    }
