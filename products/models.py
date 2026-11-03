from django.conf import settings
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify



def download_storage():
    """Where digital download files are kept.

    On Heroku: Cloudinary "raw" storage, because .zip and .pdf are not pictures.
    On your Mac: the normal media folder.
    """
    if getattr(settings, "USE_CLOUDINARY", False):
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        return RawMediaCloudinaryStorage()
    return default_storage


class Category(models.Model):
    """A group of products, for example "Sticker sets" or "Prints"."""

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="categories/", blank=True,
        help_text="Optional. If empty, the newest product picture is used.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    @property
    def cover_image(self):
        """The picture for this category on the home page.

        1. The category's own image, if the owner uploaded one.
        2. Otherwise the image of the newest active product that has one.
        3. Otherwise None, and the page shows the red sign only.
        """
        if self.image:
            return self.image
        product = (
            self.products.filter(is_active=True)
            .exclude(image="")
            .order_by("-created_at", "-pk")
            .first()
        )
        return product.image if product else None


class Product(models.Model):
    """One thing the shop sells."""

    DIGITAL = "digital"
    PRINTED = "printed"
    PORTRAIT = "portrait"
    TYPE_CHOICES = [
        (DIGITAL, "Digital download"),
        (PRINTED, "Printed item (shipped)"),
        (PORTRAIT, "Custom portrait"),
    ]

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    product_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=DIGITAL)
    image = models.ImageField(upload_to="products/", blank=True)
    download_file = models.FileField(
        upload_to="downloads/", blank=True, storage=download_storage
    )
    stock = models.PositiveIntegerField(
        default=0, help_text="Only used for printed items."
    )
    max_people = models.PositiveSmallIntegerField(
        default=1,
        help_text="Portraits: the most people or pets a customer can choose. 1 means no choice.",
    )
    extra_person_price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)],
        help_text="Portraits: added for each person or pet after the first.",
    )
    is_active = models.BooleanField(
        default=True, help_text="Untick to hide the product from the shop."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Make a web address name (slug) from the product name the first time."""
        if not self.slug:
            self.slug = self.make_unique_slug()
        super().save(*args, **kwargs)

    def make_unique_slug(self):
        """Turn "Milk Tea Set" into "milk-tea-set".

        If that is already taken, try "milk-tea-set-2", "milk-tea-set-3" and so on.
        """
        base = slugify(self.name) or "product"
        slug = base
        number = 2
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{number}"
            number += 1
        return slug

    @property
    def is_sold_out(self):
        """Only printed items can sell out. Digital files never run out."""
        return self.product_type == self.PRINTED and self.stock == 0

    @property
    def people_choices(self):
        """[1, 2, 3, ...] for the "How many people" menu."""
        return list(range(1, self.max_people + 1))

    def get_absolute_url(self):
        return reverse("products:detail", args=[self.slug])


class ProductOption(models.Model):
    """One version of a product the customer can choose.

    For example a portrait as "Digital file" or as "Printed A4, shipped".
    The final price is the product price plus the option's extra price.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="options")
    name = models.CharField(max_length=80)
    extra_price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)],
        help_text="Added to the product price. Use 0 for the basic version.",
    )
    is_printed = models.BooleanField(
        default=False, help_text="Tick if this version is printed and posted (needs shipping)."
    )
    position = models.PositiveIntegerField(default=0, help_text="Lower numbers are shown first.")

    class Meta:
        ordering = ["position", "pk"]

    def __str__(self):
        return f"{self.product.name}: {self.name}"

    @property
    def price(self):
        return self.product.price + self.extra_price


class ProductImage(models.Model):
    """An extra picture for a product, for example a finished portrait as an example."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="examples")
    image = models.ImageField(upload_to="products/examples/")
    caption = models.CharField(max_length=120, blank=True, help_text="For example: Philipp and Luca, 2026")
    position = models.PositiveIntegerField(default=0, help_text="Lower numbers are shown first.")

    class Meta:
        ordering = ["position", "pk"]

    def __str__(self):
        return self.caption or f"Example for {self.product.name}"
