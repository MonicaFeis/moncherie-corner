from django import forms

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
        label="Notes for your portrait 肖像備註",
        help_text="Who is in it, the mood, colours, anything you would like.",
    )

    def __init__(self, *args, needs_shipping=False, needs_notes=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.needs_shipping = needs_shipping
        self.needs_notes = needs_notes
        if not needs_shipping:
            del self.fields["shipping_method"]
        if not needs_notes:
            del self.fields["notes"]

    def clean(self):
        cleaned = super().clean()
        if self.needs_shipping and not cleaned.get("shipping_method"):
            self.add_error("shipping_method", "Please choose how to ship your printed items.")
        if self.needs_notes and not cleaned.get("notes", "").strip():
            self.add_error("notes", "Please tell me a little about the portrait you would like.")
        return cleaned
