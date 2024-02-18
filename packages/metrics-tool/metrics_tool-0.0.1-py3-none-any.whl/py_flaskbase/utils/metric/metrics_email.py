"""Email."""

import smtplib
from email.message import EmailMessage
from email.errors import MessageError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template
from py_flaskbase.config import get_config
from py_flaskbase.log_config import LOG, logger


def send_simple_text_email(subject: str, sender_email_address: str, recipient_email_addresses: list[str], message: str) -> None:
    """Send Simple Email.

    Arguments:
        subject {string} -- subject of email
        sender_email_address {string} -- sender's email address
        recipient_email_addresses {list} -- list of email addresses of where
                                            to send the email
        message {string} -- email message
    """
    try:
        msg = EmailMessage()
        email_server = smtplib.SMTP(get_config("MY_EMAIL_SERVER"))
        msg["Subject"] = subject
        msg.set_content(message)
        msg["From"] = sender_email_address
        msg["To"] = ", ".join(recipient_email_addresses)
        email_server.send_message(msg)
        email_server.quit()
    except MessageError as exception:
        exception = f"MessageError in metrics_email.send_simple_text_email: {exception}"
        logger().error(exception)
        raise MessageError(exception)


def send_templated_html_email(subject: str, sender_email_address: str, recipient_email_addresses: [str], template: str, **template_context):
    """Send Templated Email.

    Arguments:
        subject {string} -- subject of email
        sender_email_address {string} -- sender's email address
        recipient_email_addresses {list} -- list of email addresses of where
                                            to send the email
        template {string} -- the name of the template to be rendered. The template
                             should be located within the apps template folder defined
                             in the flask app object
        template_context -- the variables that should be available in the
                            context of the template.
    """
    try:
        html_message_body = render_template(template, **template_context)
        send_html_email(subject, sender_email_address, recipient_email_addresses, html_message_body)
    except Exception as exception:
        exception = f"Exception in metrics_email.send_templated_html_email: {exception}"
        logger().error(exception)
        raise Exception(exception)


def send_html_email(subject: str, sender_email_address: str, recipient_email_addresses: [str], html_message_body: str):
    """Send HTML Email.

    Arguments:
        subject {string} -- subject of email
        sender_email_address {string} -- sender's email address
        recipient_email_addresses {list} -- list of email addresses of where
                                            to send the email
        html_message_body {string} -- html file to be emailed
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["subject"] = subject
        msg["To"] = ", ".join(recipient_email_addresses)
        msg["From"] = sender_email_address
        msg.attach(MIMEText(html_message_body, "html"))
        email_server = smtplib.SMTP(get_config("MY_EMAIL_SERVER"))
        email_server.send_message(msg)
        email_server.quit()
    except MessageError as exception:
        exception = f"MessageError in metrics_email.send_html_email: {exception}"
        logger().error(exception)
        raise MessageError(exception)
