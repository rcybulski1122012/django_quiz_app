from django.contrib.auth import get_user_model
from django.test import SimpleTestCase

from accounts.models import Profile

User = get_user_model()


class TestProfile(SimpleTestCase):
    def test_str(self):
        user = User(
            username="User123",
            password="SecretPass123",
        )
        profile = Profile(user=user)
        profile_str = f"{user.username} profile"
        self.assertEqual(str(profile), profile_str)
