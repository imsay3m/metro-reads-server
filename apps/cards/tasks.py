from celery import shared_task
from django.core.files.base import ContentFile

from .generators import generate_library_card_pdf
from .models import LibraryCard


@shared_task
def generate_library_card_pdf_task(user_id: int, library_card_id: str) -> str:
    """
    Generate the library card PDF asynchronously and attach it to the LibraryCard.
    Returns the saved path.
    """
    # Lazy import to avoid circulars
    from apps.users.models import User

    user = User.objects.get(id=user_id)
    card = LibraryCard.objects.get(id=library_card_id)

    pdf_file = generate_library_card_pdf(user, card)
    save_path = f"library_cards/{pdf_file.name}"
    card.pdf_card.save(pdf_file.name, ContentFile(pdf_file.read()), save=True)
    return save_path
