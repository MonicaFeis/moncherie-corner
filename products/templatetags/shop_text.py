"""Template filters for shop text."""
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def description_html(text):
    """Turn a product description into safe HTML.

    A line that starts with "## " becomes a small heading, so the owner can
    write "## 價錢 Price" in the admin. Other lines keep their line breaks,
    and an empty line starts a new paragraph. Everything is escaped first.
    """
    parts = []
    lines = []

    def finish_paragraph():
        if lines:
            parts.append("<p>" + "<br>".join(lines) + "</p>")
            lines.clear()

    for raw in (text or "").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            finish_paragraph()
            parts.append('<h2 class="description-heading">' + escape(line[3:].strip()) + "</h2>")
        elif line:
            lines.append(escape(line))
        else:
            finish_paragraph()
    finish_paragraph()
    return mark_safe("\n".join(parts))
