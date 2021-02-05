from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from quizzes.models import Category, Quiz, Question


class TestRegisterView(TestCase):
    register_url = reverse('accounts:register')
    home_url = reverse('home')

    @staticmethod
    def get_example_user_data():
        return {'username': 'User123', 'email': 'emailaddress123@gmail.com',
                'password1': 'SecretPass123', 'password2': 'SecretPass123'}

    def test_status_code_is_equal_to_200_when_request_method_is_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_creates_user_and_profile_when_given_data_is_correct(self):
        data = self.get_example_user_data()
        self.client.post(self.register_url, data, follow=True)
        does_user_exist = User.objects.filter(username=data['username']).exists()
        does_profile_exist = Profile.objects.filter(user__username=data['username']).exists()
        self.assertTrue(does_user_exist)
        self.assertTrue(does_profile_exist)

    def test_redirects_to_home_page_when_given_data_is_correct(self):
        data = self.get_example_user_data()
        response = self.client.post(self.register_url, data, follow=True)
        self.assertRedirects(response, self.home_url)

    def test_displays_success_message_when_given_data_is_correct(self):
        data = self.get_example_user_data()
        response = self.client.post(self.register_url, data, follow=True)
        self.assertContains(response, 'Your account has been created successfully.')

    def test_displays_error_message_when_given_data_is_incorrect(self):
        User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')
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
                response = self.client.post(self.register_url, data=data)
                self.assertContains(response, expected_message)


class TestProfileView(TestCase):
    profile_url = reverse('accounts:profile')
    login_url = reverse('accounts:login')

    def test_redirects_to_login_page_when_user_is_not_logged(self):
        response = self.client.get(self.profile_url, follow=True)
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_url}')

    def test_updates_profile_when_data_is_correct(self):
        user = User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')
        self.client.login(username='User123', password='SecretPass123')

        self.client.post(self.profile_url, data={'description': 'New Description'})
        user.refresh_from_db()
        self.assertEqual(user.profile.description, 'New Description')

    def test_displays_success_message_when_profile_is_updated(self):
        User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')
        self.client.login(username='User123', password='SecretPass123')

        response = self.client.post(self.profile_url, data={'description': 'New Description'}, follow=True)
        self.assertContains(response, 'Your Profile has been updated successfully.')

    def test_context_contains_list_of_quizzes_created_by_user(self):
        self.category = Category.objects.create(title='Category')
        self.user1 = User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')
        self.user2 = User.objects.create_user('User124', 'addressemail124@gmail.com', 'SecretPass123')
        self.quiz = Quiz.objects.create(title='Title', category=self.category, author=self.user1)
        self.quiz = Quiz.objects.create(title='Other Quiz', category=self.category, author=self.user2)
        self.question = Question.objects.create(question='Question', quiz=self.quiz)
        self.client.login(username='User123', password='SecretPass123')

        response = self.client.get(self.profile_url)
        self.assertQuerysetEqual(response.context['quizzes'], ['<Quiz: Title>'])
