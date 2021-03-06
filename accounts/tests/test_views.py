from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.forms import SAME_EMAIL_ERROR, TOO_LONG_WORD_ERROR
from accounts.models import Profile
from accounts.views import (ACCOUNT_CREATE_SUCCESS_MESSAGE,
                            PROFILE_UPDATE_SUCCESS_MESSAGE)
from quizzes.models import Category, Quiz


class TestRegisterView(TestCase):
    register_url = reverse("accounts:register")
    home_url = reverse("home")

    @staticmethod
    def get_example_user_data():
        return {
            "username": "User123",
            "email": "emailaddress123@gmail.com",
            "password1": "SecretPass123",
            "password2": "SecretPass123",
        }

    def test_status_code_is_equal_to_200_when_request_method_is_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_creates_user_and_profile_when_given_data_is_correct(self):
        data = self.get_example_user_data()
        self.client.post(self.register_url, data, follow=True)
        does_user_exist = User.objects.filter(username=data["username"]).exists()
        does_profile_exist = Profile.objects.filter(
            user__username=data["username"]
        ).exists()
        self.assertTrue(does_user_exist)
        self.assertTrue(does_profile_exist)

    def test_redirects_to_home_page_when_given_data_is_correct(self):
        data = self.get_example_user_data()
        response = self.client.post(self.register_url, data, follow=True)
        self.assertRedirects(response, self.home_url)

    def test_displays_success_message_when_given_data_is_correct(self):
        data = self.get_example_user_data()
        response = self.client.post(self.register_url, data, follow=True)
        self.assertContains(response, ACCOUNT_CREATE_SUCCESS_MESSAGE)

    def test_displays_error_message_when_given_data_is_incorrect(self):
        User.objects.create_user(
            "User123", "addressemail123@gmail.com", "SecretPass123"
        )
        params = [
            [
                {
                    "username": "User123",
                    "email": "otheremail123@gmail.com",
                    "password1": "SecretPass123",
                    "password2": "SecretPass123",
                },
                "A user with that username already exists.",
            ],
            [
                {
                    "username": "OtherUser123",
                    "email": "addressemail123@gmail.com",
                    "password1": "SecretPass123",
                    "password2": "SecretPass123",
                },
                SAME_EMAIL_ERROR,
            ],
            [
                {
                    "username": "OtherUser123",
                    "email": "otheremail123@gmail.com",
                    "password1": "SecretPass123",
                    "password2": "OtherPassword123",
                },
                "The two password fields didn’t match.",
            ],
        ]
        for data, expected_message in params:
            with self.subTest():
                response = self.client.post(self.register_url, data=data)
                self.assertContains(response, expected_message)


class TestProfileView(TestCase):
    profile_url = reverse("accounts:profile")
    login_url = reverse("accounts:login")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            "User123", "addressemail123@gmail.com", "SecretPass123"
        )

    def setUp(self):
        self.client.login(username="User123", password="SecretPass123")

    def test_redirects_to_login_page_when_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.profile_url}")

    def test_updates_profile_when_data_is_correct(self):
        self.client.post(self.profile_url, data={"description": "New Description"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.description, "New Description")

    def test_displays_success_message_when_profile_is_updated(self):
        response = self.client.post(
            self.profile_url, data={"description": "New Description"}, follow=True
        )
        self.assertContains(response, PROFILE_UPDATE_SUCCESS_MESSAGE)

    def test_context_contains_list_of_quizzes_created_by_user(self):
        category = Category.objects.create(title="Category")
        new_user = User.objects.create_user(
            "User124", "addressemail124@gmail.com", "SecretPass123"
        )
        Quiz.objects.create(title="Title", category=category, author=self.user)
        Quiz.objects.create(title="Other Quiz", category=category, author=new_user)
        response = self.client.get(self.profile_url)
        self.assertQuerysetEqual(response.context["quizzes"], ["<Quiz: Title>"])

    def test_displays_appropriate_message_when_user_has_no_quizzes(self):
        response = self.client.get(self.profile_url)
        self.assertContains(response, "You have not created any quiz yet.")

    def test_displays_error_when_any_word_of_description_is_longer_than_45_characters(
        self,
    ):
        response = self.client.post(
            self.profile_url,
            data={
                "description": "one_very_long_word_and_that_should_raise_a_validation_error"
            },
            follow=True,
        )
        self.assertContains(response, TOO_LONG_WORD_ERROR)
