from django.shortcuts import render


def index(request):
    """Show the home page."""
    return render(request, "home/index.html")
