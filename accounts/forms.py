from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

SAME_EMAIL_ERROR = "An account with the same email already exists!"


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["email"].help_text = "Required. Must be unique."

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(SAME_EMAIL_ERROR)
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
