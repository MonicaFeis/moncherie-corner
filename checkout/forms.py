from django import forms
from django.core.validators import FileExtensionValidator

from .models import ShippingMethod


class ShipOrderForm(forms.Form):
    """The owner types the tracking number when posting an order (US-36)."""

    tracking_number = forms.CharField(
        max_length=80,
        label="Tracking number 追蹤號碼",
        error_messages={"required": "Please enter the tracking number."},
    )

    def clean_tracking_number(self):
        number = self.cleaned_data["tracking_number"].strip()
        if not number:
            raise forms.ValidationError("Please enter the tracking number.")
        return number


MAX_PORTRAIT_SIZE_MB = 20
MAX_PHOTOS = 5
MAX_PHOTO_SIZE_MB = 10


class MultiplePhotoInput(forms.ClearableFileInput):
    """A file box where the customer can pick more than one photo."""

    allow_multiple_selected = True


class MultiplePhotoField(forms.ImageField):
    """Checks every photo: it must be a real picture and not too big."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiplePhotoInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data]
        files = [file for file in files if file]
        if not files:
            if self.required:
                raise forms.ValidationError("Please add at least one photo.")
            return []
        if len(files) > MAX_PHOTOS:
            raise forms.ValidationError(f"Please send {MAX_PHOTOS} photos or fewer.")
        cleaned = []
        for file in files:
            if file.size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(f"Each photo must be smaller than {MAX_PHOTO_SIZE_MB} MB.")
            cleaned.append(super().clean(file, initial))
        return cleaned


class DeliverPortraitForm(forms.Form):
    """The owner uploads the finished portrait for one order line (US-24)."""

    portrait_file = forms.FileField(
        label="Finished portrait 完成嘅肖像",
        validators=[FileExtensionValidator(["png", "jpg", "jpeg", "pdf", "zip"])],
        help_text="A .png, .jpg, .pdf or .zip file.",
        error_messages={"required": "Please choose the file to upload."},
    )

    def clean_portrait_file(self):
        file = self.cleaned_data["portrait_file"]
        if file.size > MAX_PORTRAIT_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"Please use a file smaller than {MAX_PORTRAIT_SIZE_MB} MB.")
        return file


class CheckoutForm(forms.Form):
    """Extra details before paying. Fields are only required when they are needed."""

    shipping_method = forms.ModelChoiceField(
        queryset=ShippingMethod.objects.filter(is_active=True),
        required=False,
        empty_label="Choose how to ship 選擇運送方式",
        label="Shipping 運送",
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        label="Names and notes 名字同備註",
        help_text="Write the name of everyone (and every pet) in the portrait, as you want it written. "
        "Then anything else: the mood, colours, clothes, background.",
    )
    reference_photos = MultiplePhotoField(
        label="Photos 相片",
        help_text=f"1 to {MAX_PHOTOS} clear photos of everyone (and every pet) in the portrait.",
    )

    def __init__(self, *args, needs_shipping=False, needs_notes=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.needs_shipping = needs_shipping
        self.needs_notes = needs_notes
        if not needs_shipping:
            del self.fields["shipping_method"]
        if not needs_notes:
            del self.fields["notes"]
            del self.fields["reference_photos"]

    def clean(self):
        cleaned = super().clean()
        if self.needs_shipping and not cleaned.get("shipping_method"):
            self.add_error("shipping_method", "Please choose how to ship your printed items.")
        if self.needs_notes and not cleaned.get("notes", "").strip():
            self.add_error("notes", "Please tell me a little about the portrait you would like.")
        return cleaned
