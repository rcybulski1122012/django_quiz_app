from django.contrib.auth import get_user_model

User = get_user_model()


class QuizzesTestMixin:
    @staticmethod
    def create_user_and_return(username, email, password='SecretPass123'):
        return User.objects.create(username=username, email=email, password=password)