from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logged_out.html'), name='logout'),
    path('profile/', views.profile, name='profile'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password/change.html',
        success_url=reverse_lazy('accounts:password_change_done')), name='password_change'),
    path('password_change_done/,', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password/change_done.html'), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password/reset_form.html',
        email_template_name='accounts/password/reset_email.html',
        subject_template_name='accounts/password/reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done')), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password/reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password/reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete')), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password/change_done.html'), name='password_reset_complete'),
]
