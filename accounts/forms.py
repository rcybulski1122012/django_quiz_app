from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from accounts.models import Profile
from common.utils import is_too_long_word_in_text

SAME_EMAIL_ERROR = "An account with the same email already exists!"
TOO_LONG_WORD_ERROR = "Any word should not be longer than 45 characters."


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["description", "photo"]

    def clean_description(self):
        description = self.cleaned_data["description"]
        if is_too_long_word_in_text(description):
            raise forms.ValidationError(TOO_LONG_WORD_ERROR)
        return description
