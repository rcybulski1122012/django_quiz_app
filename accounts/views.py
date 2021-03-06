from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.forms import ProfileForm, UserRegistrationForm
from accounts.models import Profile

User = get_user_model()

ACCOUNT_CREATE_SUCCESS_MESSAGE = "Your account has been created successfully."
PROFILE_UPDATE_SUCCESS_MESSAGE = "Your Profile has been updated successfully."


class RegisterView(SuccessMessageMixin, CreateView):
    model = User
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("home")
    success_message = ACCOUNT_CREATE_SUCCESS_MESSAGE


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")
    success_message = PROFILE_UPDATE_SUCCESS_MESSAGE

    def get_object(self, **kwargs):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quizzes"] = self.request.user.quizzes.all()
        return context
