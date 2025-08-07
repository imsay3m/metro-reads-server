import os
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from PIL import Image  # Ensure this import is present
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def generate_library_card_pdf(user, card):
    """
    Generates a PDF library card. This version uses a robust method for handling
    the QR code image by saving it to a temporary file before drawing.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Card Layout ---
    card_width, card_height = 5 * inch, 3 * inch
    x_offset, y_offset = (width - card_width) / 2, (height - card_height) / 2
    p.rect(x_offset, y_offset, card_width, card_height)

    # --- Branding ---
    # This uses the 'user_avatar.png' file you mentioned.
    # Change 'user_avatar.png' to 'logo.png' if you have renamed the file.
    # Fallback for STATICFILES_DIRS if not set or empty (Docker compatibility)
    static_dirs = getattr(settings, "STATICFILES_DIRS", [])
    if static_dirs:
        logo_path = os.path.join(static_dirs[0], "user_avatar.png")
    else:
        logo_path = os.path.join(settings.STATIC_ROOT, "user_avatar.png")
    if os.path.exists(logo_path):
        p.drawImage(
            logo_path,
            x_offset + 0.2 * inch,
            y_offset + card_height - 1.2 * inch,
            width=1 * inch,
            height=1 * inch,
            preserveAspectRatio=True,
            mask="auto",
        )

    p.setFont("Helvetica-Bold", 24)
    p.drawString(
        x_offset + 1.5 * inch, y_offset + card_height - 0.7 * inch, "Metro Reads"
    )
    p.setFont("Helvetica", 12)
    p.drawString(
        x_offset + 1.5 * inch,
        y_offset + card_height - 1 * inch,
        "Library Membership Card",
    )

    # --- User Details ---
    p.setFont("Helvetica", 12)
    p.drawString(
        x_offset + 0.3 * inch,
        y_offset + 1.5 * inch,
        f"Member: {user.first_name} {user.last_name}",
    )
    p.drawString(x_offset + 0.3 * inch, y_offset + 1.2 * inch, f"Card ID: {card.id}")
    p.drawString(
        x_offset + 0.3 * inch,
        y_offset + 0.9 * inch,
        f"Expires: {card.expiry_date.strftime('%Y-%m-%d')}",
    )

    # --- QR Code (Robust Method: Save as PNG and use file path) ---
    qr_data = str(user.id)
    qr_code_img = qrcode.make(qr_data)
    with NamedTemporaryFile(delete=True, suffix=".png") as img_temp:
        qr_code_img.save(img_temp, format="PNG")
        img_temp.flush()
        p.drawImage(
            img_temp.name,
            x_offset + card_width - 1.5 * inch,
            y_offset + 0.5 * inch,
            width=1.2 * inch,
            height=1.2 * inch,
            preserveAspectRatio=True,
            mask="auto",
        )

    # --- Finalize PDF ---
    p.showPage()
    p.save()

    buffer.seek(0)

    file_name = f"library_card_{user.id}.pdf"
    pdf_file = ContentFile(buffer.getvalue(), name=file_name)

    return pdf_file
    pdf_file = ContentFile(buffer.getvalue(), name=file_name)

    return pdf_file
