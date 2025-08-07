from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.books.models import Book
from apps.loans.models import Loan
from apps.queues.models import BookQueue
from apps.users.models import User


def get_dashboard_context():
    """
    Gathers all KPI and widget data for the admin dashboard.
    """
    # --- KPI Calculations ---
    total_members = User.objects.filter(role=User.Role.MEMBER).count()
    active_loans = Loan.objects.filter(is_returned=False).count()
    overdue_books = Loan.objects.filter(
        due_date__lt=timezone.now(), is_returned=False
    ).count()
    books_with_queues = (
        Book.objects.filter(queues__status=BookQueue.QueueStatus.ACTIVE)
        .distinct()
        .count()
    )

    # --- Widget Data ---
    recently_returned = Loan.objects.filter(is_returned=True).order_by("-return_date")[
        :5
    ]
    most_overdue = Loan.objects.filter(
        is_returned=False, due_date__lt=timezone.now()
    ).order_by("due_date")[:5]
    top_queued_books = (
        Book.objects.annotate(
            active_queue_count=Count(
                "queues", filter=Q(queues__status=BookQueue.QueueStatus.ACTIVE)
            )
        )
        .filter(active_queue_count__gt=0)
        .order_by("-active_queue_count")[:5]
    )

    # --- Chart Data ---
    seven_days_ago = timezone.now() - timedelta(days=7)
    loans_last_7_days = Loan.objects.filter(loan_date__gte=seven_days_ago)
    loan_counts_by_day = {}
    for i in range(7):
        day = (timezone.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        loan_counts_by_day[day] = 0
    for loan in loans_last_7_days:
        day_str = loan.loan_date.strftime("%Y-%m-%d")
        if day_str in loan_counts_by_day:
            loan_counts_by_day[day_str] += 1
    chart_labels = list(reversed(loan_counts_by_day.keys()))
    chart_data = list(reversed(loan_counts_by_day.values()))

    # New context variable to handle the "No Data" message for the chart
    total_loans_this_week = sum(chart_data)

    return {
        "total_members": total_members,
        "active_loans": active_loans,
        "overdue_books": overdue_books,
        "books_with_queues": books_with_queues,
        "recently_returned": recently_returned,
        "most_overdue": most_overdue,
        "top_queued_books": top_queued_books,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "total_loans_this_week": total_loans_this_week,
    }
