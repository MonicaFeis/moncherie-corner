"""All emails the shop sends.

Every email uses 3 template files in notifications/templates/notifications/:
- <name>_subject.txt  (the subject line)
- <name>.txt          (plain text version)
- <name>.html         (nice-looking version)
More emails (order confirmed, payment failed, shipped) are added
when we build the checkout app.
"""
import logging
import smtplib

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_email(to_address, template_name, context):
    """Build one email from its 3 templates and send it.

    Returns True if it was sent, False if the email server had a problem.
    A mail problem should never break the page the customer is on.
    """
    context = {**context, "site_url": settings.SITE_URL}
    folder = "notifications"
    subject = render_to_string(f"{folder}/{template_name}_subject.txt", context).strip()
    text_body = render_to_string(f"{folder}/{template_name}.txt", context)
    html_body = render_to_string(f"{folder}/{template_name}.html", context)

    message = EmailMultiAlternatives(
        subject, text_body, settings.DEFAULT_FROM_EMAIL, [to_address]
    )
    message.attach_alternative(html_body, "text/html")

    try:
        message.send()
    except (smtplib.SMTPException, OSError):
        logger.exception("Could not send the %s email to %s", template_name, to_address)
        return False
    return True


def send_welcome_email(user):
    """Send a welcome email after someone registers (US-39)."""
    return send_email(user.email, "welcome", {"user": user})
