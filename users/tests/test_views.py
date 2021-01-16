from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from common.test_utils import QuizzesTestMixin

User = get_user_model()


class TestRegisterView(QuizzesTestMixin, TestCase):
    view_url = reverse('users:register')

    def test_when_request_method_is_get_status_code_should_be_equal_200(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)

    def test_when_request_method_is_post_and_data_is_correct_should_create_account(self):
        data = {'username': 'User123', 'email': 'emailaddress123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}
        self.client.post(self.view_url, data, follow=True)
        does_user_exist = User.objects.filter(username=data['username']).exists()
        self.assertTrue(does_user_exist)

    def test_when_request_method_is_post_and_data_is_correct_should_redirect_to_home_page(self):
        data = {'username': 'User123', 'email': 'emailaddress123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}
        response = self.client.post(self.view_url, data, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_when_request_method_is_post_and_data_is_correct_should_display_success_message(self):
        data = {'username': 'User123', 'email': 'emailaddress123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}
        response = self.client.post(self.view_url, data, follow=True)
        self.assertContains(response, 'Your account has been created successfully!')

    def test_when_request_method_is_post_and_data_is_incorrect_should_display_error(self):
        self.create_user_and_return(username='Username123', email='addressemail123@gmail.com')

        # Same username error
        data = {'username': 'Username123', 'email': 'otheremail123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}
        response = self.client.post(self.view_url, data)
        self.assertContains(response, 'A user with that username already exists.')

        # Same email error
        data = {'username': 'OtherUsername123', 'email': 'addressemail123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}
        response = self.client.post(self.view_url, data)
        self.assertContains(response, 'An account with the same email already exists!')

        # Not matching passwords
        data = {'username': 'OtherUsername123', 'email': 'otheremail123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'OtherPassword123'}
        response = self.client.post(self.view_url, data)
        self.assertContains(response, 'The two password fields didn’t match.')
