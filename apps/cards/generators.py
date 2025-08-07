import os
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4  # Import A4 page size
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def generate_library_card_pdf(user, card):
    """
    Generates a professional, two-sided PDF library card on an A4 page,
    with branding and colors that match the email templates.
    """
    buffer = BytesIO()
    # Set page size to A4
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # Get A4 dimensions

    # --- BRANDING AND COLOR PALETTE (from email template) ---
    brand_dark_blue = colors.HexColor("#1e3a5f")
    brand_light_blue = colors.HexColor("#2c5aa0")
    background_gray = colors.HexColor("#f8f9fa")
    text_light = colors.HexColor("#ffffff")
    text_dark = colors.HexColor("#333333")
    text_secondary = colors.HexColor("#555555")

    card_width, card_height = 3.375 * inch, 2.125 * inch  # Standard ID card size

    # --- CARD FRONT (Centered on the top half of the A4 page) ---
    x_offset = (width - card_width) / 2
    y_offset = height / 2 + 0.5 * inch  # Position in the top half

    # Card background with a subtle border
    p.setFillColor(background_gray)
    p.setStrokeColor(brand_dark_blue)
    p.roundRect(
        x_offset, y_offset, card_width, card_height, 0.15 * inch, fill=1, stroke=1
    )

    # Header bar
    p.setFillColor(brand_dark_blue)
    p.roundRect(
        x_offset,
        y_offset + card_height - 0.6 * inch,
        card_width,
        0.6 * inch,
        0.15 * inch,
        fill=1,
        stroke=0,
    )

    # Header Text (smaller font)
    p.setFillColor(text_light)
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(
        x_offset + card_width / 2, y_offset + card_height - 0.3 * inch, "Metro Reads"
    )
    p.setFont("Helvetica", 7)
    p.drawCentredString(
        x_offset + card_width / 2,
        y_offset + card_height - 0.45 * inch,
        "LIBRARY MEMBERSHIP CARD",
    )

    # User Photo with Fallback (smaller size)
    photo_size = 0.7 * inch
    photo_x = x_offset + 0.2 * inch
    photo_y = y_offset + 0.2 * inch

    photo_path = None
    if (
        user.profile_picture
        and hasattr(user.profile_picture, "path")
        and os.path.exists(user.profile_picture.path)
    ):
        photo_path = user.profile_picture.path

    if not photo_path:
        # Fallback to user_avatar.png
        static_dirs = getattr(settings, "STATICFILES_DIRS", [])
        avatar_path = (
            os.path.join(static_dirs[0], "user_avatar.png")
            if static_dirs
            else os.path.join(settings.STATIC_ROOT, "user_avatar.png")
        )
        if os.path.exists(avatar_path):
            photo_path = avatar_path

    # Draw photo frame
    p.setStrokeColor(brand_light_blue)
    p.setLineWidth(1.5)
    p.roundRect(
        photo_x - 0.05 * inch,
        photo_y - 0.05 * inch,
        photo_size + 0.1 * inch,
        photo_size + 0.1 * inch,
        0.1 * inch,
        fill=0,
        stroke=1,
    )

    if photo_path:
        try:
            p.drawImage(
                photo_path,
                photo_x,
                photo_y,
                width=photo_size,
                height=photo_size,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            p.setFont("Helvetica", 8)
            p.drawCentredString(
                photo_x + photo_size / 2, photo_y + photo_size / 2 - 4, "Photo N/A"
            )

    # User Details (smaller font, add email and unique 8-char ID)
    details_x = photo_x + photo_size + 0.18 * inch
    details_y_start = photo_y + photo_size - 0.10 * inch
    p.setFillColor(text_dark)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(details_x, details_y_start, f"{user.first_name} {user.last_name}")

    p.setFillColor(text_secondary)
    p.setFont("Helvetica", 7)
    p.drawString(details_x, details_y_start - 0.18 * inch, f"Email: {user.email}")
    p.drawString(details_x, details_y_start - 0.32 * inch, f"Member ID: {user.id}")
    # Unique 8-char card ID
    unique_id = str(card.id)[:8].zfill(8)
    p.drawString(details_x, details_y_start - 0.46 * inch, f"Card #: {unique_id}")
    p.drawString(
        details_x,
        details_y_start - 0.60 * inch,
        f"Expires: {card.expiry_date.strftime('%m / %Y')}",
    )

    # --- CARD BACK (Centered on the bottom half of the A4 page) ---
    x_offset_back = (width - card_width) / 2
    y_offset_back = height / 2 - card_height - 0.5 * inch  # Position in the bottom half

    p.setFillColor(colors.white)
    p.setStrokeColor(brand_dark_blue)
    p.roundRect(
        x_offset_back,
        y_offset_back,
        card_width,
        card_height,
        0.15 * inch,
        fill=1,
        stroke=1,
    )

    # Magnetic Stripe Placeholder
    p.setFillColor(colors.black)
    p.rect(
        x_offset_back,
        y_offset_back + card_height - 0.5 * inch,
        card_width,
        0.4 * inch,
        fill=1,
        stroke=0,
    )

    # QR Code on the back (centered, just below headline area)
    qr_code = qr.QrCodeWidget(f"{settings.FRONTEND_BASE_URL}/users/{user.id}/")
    bounds = qr_code.getBounds()
    width_qr, height_qr = bounds[2] - bounds[0], bounds[3] - bounds[1]
    qr_size = 0.9 * inch
    d = Drawing(
        qr_size,
        qr_size,
        transform=[qr_size / width_qr, 0, 0, qr_size / height_qr, 0, 0],
    )
    d.add(qr_code)
    qr_x = x_offset_back + (card_width - qr_size) / 2
    headline_y = y_offset_back + card_height - 0.55 * inch
    qr_y = headline_y - qr_size - 0.05 * inch
    renderPDF.draw(d, p, qr_x, qr_y)

    # Library Information (centered, below QR code)
    info_text_y = qr_y - 0.15 * inch
    p.setFillColor(text_secondary)
    p.setFont("Helvetica-Bold", 7)
    p.drawCentredString(
        x_offset_back + card_width / 2,
        info_text_y,
        "www.metroreads.com | info@metroreads.com",
    )

    # Additional info text (centered, below the above line)
    p.setFont("Helvetica", 7)
    p.drawCentredString(
        x_offset_back + card_width / 2,
        info_text_y - 0.15 * inch,
        "This card is the property of Metro Reads Library.",
    )
    p.drawCentredString(
        x_offset_back + card_width / 2,
        info_text_y - 0.30 * inch,
        "A lost or stolen card should be reported immediately.",
    )

    # --- Finalize PDF ---
    p.showPage()
    p.save()

    buffer.seek(0)
    file_name = f"library_card_{user.id}.pdf"
    pdf_file = ContentFile(buffer.getvalue(), name=file_name)

    return pdf_file
    return pdf_file
