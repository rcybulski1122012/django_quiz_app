from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from accounts.forms import ProfileForm, UserRegistrationForm


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


class TestProfileForm(SimpleTestCase):
    def test_valid_form(self):
        data = {"description": "few words which any is not longer than 45 characters"}
        form = ProfileForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_when_any_word_of_description_is_longer_than_45_characters(self):
        data = {
            "description": "one_very_long_word_and_that_should_raise_a_validation_error"
        }
        form = ProfileForm(data)
        self.assertFalse(form.is_valid())
