import os

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_metro_reads_email(subject, template_name, context, recipient_list):
    """
    A utility function to send styled HTML emails using a template.

    Args:
        subject (str): The email subject.
        template_name (str): The path to the email template file.
        context (dict): The context data to render in the template.
        recipient_list (list): A list of recipient email addresses.
    """
    try:
        # Render the HTML content from the template
        html_message = render_to_string(template_name, context)

        # Create a plain text version of the email for clients that don't render HTML
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=f"Metro Reads <{settings.EMAIL_HOST_USER}>",
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Email sent successfully to {recipient_list}")
        return True
    except Exception as e:
        # In a real app, you would log this error
        print(f"Error sending email to {recipient_list}: {e}")
        return False


def upload_image_to_imgbb(image_file):
    """
    Uploads an image file to imgbb and returns the image URL.
    """
    imgbb_api_key = os.getenv("IMGBB_API_KEY")
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": imgbb_api_key,
        "image": image_file.read(),
    }
    response = requests.post(
        url, files={"image": image_file}, data={"key": imgbb_api_key}
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["url"]
