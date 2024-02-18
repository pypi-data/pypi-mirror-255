from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Union
import octk

def create_email_file(
        recipients:list[str],
        body="",
        subject_text:str="",
        out_path:Optional[Union[str,Path]]=None,
        attachments:Optional[list[Union[str,Path]]]=None,
        # is_draft=True,
        overwrite:bool=False,
):
    if attachments is None:
        attachments=[]
    if out_path is None:
        if not subject_text:
            out_path="email.eml"
        else:
            out_path=subject_text 
    out_path=octk.uniquify(out_path)
    msg = EmailMessage()
    msg['Subject'] = subject_text
    msg['To'] = ', '.join([x.strip() for x in recipients])
    msg.set_content(body)
    # msg.preamble = 'This is a multi-part message in MIME format. You will not see this in a MIME-aware mail reader\n.'

    for attachment in attachments:
        with open(attachment, 'rb') as fp:
            attachment_bytes =  fp.read()
            
        msg.add_attachment(
            attachment_bytes,
            maintype='application', 
            subtype='xlsx', 
            filename=Path(attachment).name
            )

    msg.add_header('X-Unsent', '1')

    with open(out_path, 'wb') as outfile:
        outfile.write(bytes(msg))

from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def create_email_file_2(
        out_path:Optional[Union[str,Path]]=None,
        subject_text:str="",
        recipients:list[str]=[],
        body="",
        attachments:Optional[list[Union[str,Path]]]=None,
        overwrite=False,
):
    """
    Another method of creating an email file I found, 
    that I'm leaving here for reference

    The html format is one drawback i've noticed so far (i.e. you cannot rely 
    on the normal newline character.SS)
    """
    if out_path is None:
        out_path = r'email_sample.eml'
    if not overwrite:
        out_path = octk.uniquify(out_path)
    
    msg            = MIMEMultipart('alternative')
    msg['Subject'] = subject_text
    msg['To']      = ', '.join([x.strip() for x in recipients])

    html = f"""\
    <html>
        <head></head>
        <body>{body}</body>
    </html>"""

    part = MIMEText(html, 'html')
    msg.attach(part)
    msg.add_header('X-Unsent', '1')
    # msg.attach

    with open(out_path, 'w') as fp:
        gen = generator.Generator(fp)
        gen.flatten(msg)