from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from products.models import Product

from .forms import ReviewForm
from .models import Review
from .utils import has_bought, icon_for, question_for


def next_page(request, product):
    """Where to go after saving: back where the customer came from (only pages on this site)."""
    next_url = request.GET.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return product.get_absolute_url()


@login_required
def add_review(request, slug):
    """A page to review something you bought: opened from My downloads or your order (US-16)."""
    product = get_object_or_404(Product, slug=slug)
    if not has_bought(request.user, product):
        messages.error(request, "Only customers who bought this can review it.")
        return redirect(product.get_absolute_url())
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.info(request, "You already reviewed this. You can edit your review.")
        return redirect(product.get_absolute_url())

    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, "多謝你嘅評語 ❤️ Thank you for your review!")
        return redirect(next_page(request, product))

    context = {"form": form, "product": product, "question": question_for(product.product_type), "icon": icon_for(product.product_type)}
    return render(request, "reviews/review_add.html", context)


@login_required
def edit_review(request, pk):
    """Change your own review. Someone else's review gives a 404 (US-17)."""
    review = get_object_or_404(Review, pk=pk, user=request.user)
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "多謝你嘅評語 ❤️ Thank you for your review!")
        return redirect(review.product.get_absolute_url())
    return render(request, "reviews/review_form.html", {"form": form, "review": review})


@login_required
def delete_review(request, pk):
    """Ask first, then delete your own review (US-17)."""
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == "POST":
        product = review.product
        review.delete()
        messages.success(request, "已刪除 Your review was deleted.")
        return redirect(product.get_absolute_url())
    return render(request, "reviews/review_confirm_delete.html", {"review": review})
