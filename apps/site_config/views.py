from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone

from apps.books.models import Book
from apps.loans.models import Loan
from apps.queues.models import BookQueue
from apps.users.models import User


@staff_member_required
def dashboard(request):
    # KPIs
    total_members = User.objects.filter(role=User.Role.MEMBER).count()
    active_loans = Loan.objects.filter(is_returned=False).count()
    overdue_books = Loan.objects.filter(
        is_returned=False, due_date__lt=timezone.now()
    ).count()
    books_with_queues = (
        Book.objects.filter(queues__status=BookQueue.QueueStatus.ACTIVE)
        .distinct()
        .count()
    )

    # Chart data (example: loans per day for last 7 days)
    last_7_days = [
        timezone.now().date() - timezone.timedelta(days=i) for i in range(6, -1, -1)
    ]
    chart_labels = [d.strftime("%a") for d in last_7_days]
    chart_data = [Loan.objects.filter(loan_date__date=d).count() for d in last_7_days]

    # Top 5 queued books
    top_queued_books = (
        Book.objects.annotate(
            active_queue_count=models.Count(
                "queues", filter=models.Q(queues__status=BookQueue.QueueStatus.ACTIVE)
            )
        )
        .filter(active_queue_count__gt=0)
        .order_by("-active_queue_count")[:5]
    )

    # Most overdue loans
    most_overdue = Loan.objects.filter(
        is_returned=False, due_date__lt=timezone.now()
    ).order_by("due_date")[:5]

    # Recently returned
    recently_returned = Loan.objects.filter(is_returned=True).order_by("-return_date")[
        :5
    ]

    context = {
        "total_members": total_members,
        "active_loans": active_loans,
        "overdue_books": overdue_books,
        "books_with_queues": books_with_queues,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "top_queued_books": top_queued_books,
        "most_overdue": most_overdue,
        "recently_returned": recently_returned,
    }
    return render(request, "admin/index.html", context)
