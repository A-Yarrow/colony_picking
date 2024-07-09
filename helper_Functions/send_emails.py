
import os
import pandas as pd
import json
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv
from utils import get_env_var, export_csv


# set key credentials file path
load_dotenv()
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY') #get_env_var('SENDGRID_API_KEY')

def send_email_with_attachment(from_email, to_emails, subject, html_content, attachment_object, file_type, filename):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content)

    #encoded = attachment_object.encode()
    #encoded = base64.b64encode(attachment_object).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(attachment_object)
    attachment.file_type = FileType(file_type)
    attachment.file_name = FileName(filename)
    attachment.disposition = Disposition('attachment')
    attachment.content_id = ContentId('Example Content ID')
    message.attachment = attachment
    try:
        sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print('Here is the exception: %s' %e.message)

def send_email(from_email, to_emails:list, subject: str, body: str='Body of test email') -> None:

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=body)
    
    sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sendgrid_client.send(message)

    if response.status_code != 202:
        print("Error sending email: %s" %response.status_code)
        print("Response headers: %s" %response.headers)
        print("Response body: %s" %response.body)
        return None
    print("Email sent successfully!")


from_email = "GETC-ColonyPickDashboard@arcinstitute.org"
to_emails = [
    ('yarrowm@arcinstitute.org', 'Yarrow'),
    ('janiceh@arcinstitute.org', 'Janice')
    ]
subject = 'Test'
body = 'Test Text'
send_email(from_email, to_emails, subject, body)
#Code below is for testing the attachement function
"""
from_email = "geneengineering_tech@arcinstitute.org"
to_emails = ("yarrowm@arcinstitute.org", "janiceh@arcinstitute.org")
subject = "test subject"
html_content = "test html content"
attachment_object = export_csv(pd.DataFrame.from_dict({'A':['Elmo', 'fudge', 'rocker'], 'B':['Animal', 'bug', 'insect']}))
file_type = 'test/csv'
filename = 'test_dataframe'
send_email_with_attachment(from_email, to_emails, subject, html_content, attachment_object, file_type, filename)
"""