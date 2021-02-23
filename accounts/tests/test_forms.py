from django.contrib.auth.models import User
from django.test import TestCase

from accounts.forms import UserRegistrationForm


class TestUserRegistrationForm(TestCase):
    @staticmethod
    def get_example_form_data(
        username="User123",
        email="emailaddress123@gmail.com",
        p1="SecretPass123",
        p2="SecretPass123",
    ):
        return {"username": username, "email": email, "password1": p1, "password2": p2}

    def test_valid(self):
        data = self.get_example_form_data()
        form = UserRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_when_account_with_the_same_email_already_exists(self):
        User.objects.create_user(
            "FirstUser", "emailaddress123@gmail.com", "SecretPas123"
        )
        data = self.get_example_form_data(username="SecondUser")
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_passwords_do_not_match(self):
        data = self.get_example_form_data(p2="PasswordThatDoesNotMatch123")
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_is_invalid_when_account_with_the_same_username_already_exists(self):
        User.objects.create_user("User123", "emailaddress123@gmail.com", "SecretPas123")
        data = self.get_example_form_data()
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_is_invalid_when_email_is_not_given(self):
        data = self.get_example_form_data(email="")
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
