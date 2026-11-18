"""Template filter for product pictures."""
from django import template

register = template.Library()


@register.filter
def sized(url, width):
    """Ask Cloudinary for a picture that is only as wide as needed.

    f_auto sends WebP or AVIF to browsers that can show it, q_auto keeps the
    file small, and w_ sets the width. Pictures that are not on Cloudinary
    (for example on your Mac) stay as they are.
    """
    marker = "/image/upload/"
    url = str(url)
    if "res.cloudinary.com" not in url or marker not in url:
        return url
    return url.replace(marker, f"{marker}f_auto,q_auto,w_{width}/", 1)
