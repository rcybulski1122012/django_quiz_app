from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class QuizzesTestMixin:
    register_view_url = reverse('accounts:register')
    profile_view_url = reverse('accounts:profile')
    login_view_url = reverse('accounts:login')
    logout_view_url = reverse('accounts:logout')
    home_url = reverse('home')

    @staticmethod
    def create_user_and_return(username, email, password='SecretPass123'):
        return User.objects.create_user(username=username, email=email, password=password)
