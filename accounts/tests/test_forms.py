from django.test import TestCase

from accounts.forms import UserRegistrationForm
from common.test_utils import QuizzesTestMixin


class TestUserRegistrationForm(QuizzesTestMixin, TestCase):
    def test_valid_form(self):
        data = {
            'username': 'User123',
            'email': 'emailaddress123@gmail.com',
            'password1': 'SecretPass123',
            'password2': 'SecretPass123',
        }
        form = UserRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_when_email_is_already_in_database_form_should_be_invalid(self):
        self.create_user_and_return(username='FirstUser', email='emailaddress123@gmail.com')
        data = {
            'username': 'SecondUser',
            'email': 'emailaddress123@gmail.com',
            'password1': 'SecretPass123',
            'password2': 'SecretPass123',
        }
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_when_passwords_do_not_match_form_should_me_invalid(self):
        data = {
            'username': 'SecondUser',
            'email': 'emailaddress123@gmail.com',
            'password1': 'SecretPass123',
            'password2': 'SecretPass124',
        }
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_when_username_is_already_in_database_form_should_be_invalid(self):
        self.create_user_and_return(username='User123', email='emailaddress321@gmail.com')
        data = {
            'username': 'User123',
            'email': 'emailaddress123@gmail.com',
            'password1': 'SecretPass123',
            'password2': 'SecretPass123',
        }
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_when_email_is_not_given_form_should_be_invalid(self):
        data = {
            'username': 'User123',
            'email': None,
            'password1': 'SecretPass123',
            'password2': 'SecretPass123',
        }
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
