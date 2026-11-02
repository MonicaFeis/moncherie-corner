from django import forms
from django.core.validators import FileExtensionValidator

from .models import Product

MAX_IMAGE_SIZE_MB = 5


class ProductForm(forms.ModelForm):
    """The owner's form to add or edit a product (US-18, US-19)."""

    download_file = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(["zip", "pdf", "png", "jpg", "jpeg"])],
        help_text="Digital products only: a .zip, .pdf, .png or .jpg file.",
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "product_type",
            "price",
            "description",
            "image",
            "download_file",
            "stock",
            "max_people",
            "extra_person_price",
            "is_active",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only portraits use these, so they can be left empty
        self.fields["max_people"].required = False
        self.fields["extra_person_price"].required = False

    def clean_max_people(self):
        return self.cleaned_data.get("max_people") or 1

    def clean_extra_person_price(self):
        return self.cleaned_data.get("extra_person_price") or 0

    def clean_image(self):
        """Stop very big images, so pages stay fast."""
        image = self.cleaned_data.get("image")
        if image and image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"Please use an image smaller than {MAX_IMAGE_SIZE_MB} MB.")
        return image

    def clean(self):
        """Checks that need more than one field."""
        cleaned = super().clean()
        product_type = cleaned.get("product_type")
        has_file = cleaned.get("download_file") or self.instance.download_file
        if product_type == Product.DIGITAL and not has_file:
            self.add_error("download_file", "A digital product needs a file to download.")
        return cleaned
