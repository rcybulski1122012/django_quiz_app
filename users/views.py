from django.contrib import messages
from django.shortcuts import render, redirect

from users.forms import UserRegistrationForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!', extra_tags='alert alert-success')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})
