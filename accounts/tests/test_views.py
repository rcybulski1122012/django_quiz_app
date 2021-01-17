from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Profile
from common.test_utils import QuizzesTestMixin

User = get_user_model()


class TestRegisterView(QuizzesTestMixin, TestCase):
    def test_when_request_method_is_get_status_code_should_be_equal_200(self):
        response = self.client.get(self.register_view_url)
        self.assertEqual(response.status_code, 200)

    def test_when_request_method_is_post_and_data_is_correct_should_create_user_and_profile(self):
        data = {'username': 'User123', 'email': 'emailaddress123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}
        self.client.post(self.register_view_url, data, follow=True)
        does_user_exist = User.objects.filter(username=data['username']).exists()
        does_profile_exist = Profile.objects.filter(user__username=data['username']).exists()
        self.assertTrue(does_user_exist)
        self.assertTrue(does_profile_exist)

    def test_when_request_method_is_post_and_data_is_correct_should_redirect_to_home_page(self):
        data = {'username': 'User123', 'email': 'emailaddress123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}
        response = self.client.post(self.register_view_url, data, follow=True)
        self.assertRedirects(response, self.home_url)

    def test_when_request_method_is_post_and_data_is_correct_should_display_success_message(self):
        data = {'username': 'User123', 'email': 'emailaddress123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}
        response = self.client.post(self.register_view_url, data, follow=True)
        self.assertContains(response, 'Your account has been created successfully.')

    def test_when_request_method_is_post_and_data_is_incorrect_should_display_error(self):
        self.create_user_and_return(username='User123', email='addressemail123@gmail.com')
        params = [
            [{'username': 'User123', 'email': 'otheremail123@gmail.com',
              'password1': 'SecretPass123', 'password2': 'SecretPass123'},
             'A user with that username already exists.'],
            [{'username': 'OtherUser123', 'email': 'addressemail123@gmail.com',
              'password1': 'SecretPass123', 'password2': 'SecretPass123'},
             'An account with the same email already exists!'],
            [{'username': 'OtherUser123', 'email': 'otheremail123@gmail.com',
              'password1': 'SecretPass123', 'password2': 'OtherPassword123'},
             'The two password fields didn’t match.'],
        ]

        for data, expected_message in params:
            with self.subTest():
                response = self.client.post(self.register_view_url, data=data)
                self.assertContains(response, expected_message)


class TestProfileView(QuizzesTestMixin, TestCase):
    def test_when_user_is_not_logged_should_return_302(self):
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.status_code, 302)

    def test_when_request_method_is_post_and_data_is_correct_should_update_profile(self):
        user = self.create_user_and_return(username='User123', email='addressemail123@gmail.com',
                                           password='SecretPass123')
        self.client.login(username='User123', password='SecretPass123')
        self.client.post(self.profile_view_url, data={'description': 'New Description'})
        user.refresh_from_db()
        self.assertEqual(user.profile.description, 'New Description')

    def test_when_the_profile_has_been_updated_should_display_success_message(self):
        self.create_user_and_return(username='User123', email='addressemail123@gmail.com',
                                    password='SecretPass123')
        self.client.login(username='User123', password='SecretPass123')
        response = self.client.post(self.profile_view_url, data={'description': 'New Description'})
        self.assertContains(response, 'Your Profile has been updated successfully.')
