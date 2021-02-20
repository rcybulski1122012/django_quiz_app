from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.forms import UserRegistrationForm
from accounts.models import Profile

User = get_user_model()

ACCOUNT_CREATE_SUCCESS_MESSAGE = 'Your account has been created successfully.'
PROFILE_UPDATE_SUCCESS_MESSAGE = 'Your Profile has been updated successfully.'


class RegisterView(CreateView):
    model = User
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, ACCOUNT_CREATE_SUCCESS_MESSAGE, extra_tags='alert alert-success')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['description', 'photo']
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, **kwargs):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quizzes'] = self.request.user.quizzes.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, PROFILE_UPDATE_SUCCESS_MESSAGE, extra_tags='alert alert-success')
        return super().form_valid(form)
