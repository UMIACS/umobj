#!/usr/bin/env python

# cribbed from http://stackoverflow.com/a/3363254

import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

COMMASPACE = ', '


def send_email(send_from, send_to, subject, body_text, files=None,
               server='smtp.umiacs.umd.edu'):
    '''
    Send an email that can take an attachment

    The following args are required:
        send_from - a string
        send_to - a list of recipients
        subject - a string
        body_text - a string

    The following args are optional:
        files - a list of filenames to append as attachments to the message
        server - the SMTP server that will deliver the mail.
                 Defaults to smtp.umiacs.umd.edu
    '''
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Subject'] = subject

    msg.attach(MIMEText(body_text))

    if files is not None:
        for f in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(f, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
