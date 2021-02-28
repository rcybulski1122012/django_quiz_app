from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class TestCreateProfile(TestCase):
    def test_creates_profile_when_user_is_created(self):
        user = User.objects.create(username="User123", password="SecretPass123")
        self.assertTrue(user.profile is not None)
