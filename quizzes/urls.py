from django.urls import path
from quizzes import views

app_name = 'quizzes'

urlpatterns = [
    path('create/', views.create_quiz, name='create'),
]