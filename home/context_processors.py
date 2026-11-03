"""Small values every page can use."""
from django.utils import timezone

SUMMER_MONTHS = range(6, 11)  # June to October


def drink_for_month(month):
    """Iced bubble milk tea in summer, hot milk tea the rest of the year."""
    return "🧋" if month in SUMMER_MONTHS else "☕"


def season(request):
    """Makes {{ season_drink }} available in every template."""
    return {"season_drink": drink_for_month(timezone.localdate().month)}
