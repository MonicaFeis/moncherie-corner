from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """Sign-up form: Django's normal form, plus an email that must be unique."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        """Stop two accounts using the same email address."""
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "呢個電郵已經有帳戶。 An account with this email already exists."
            )
        return email