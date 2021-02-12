from django.urls import path
from quizzes import views

app_name = 'quizzes'

urlpatterns = [
    path('create/', views.create_quiz, name='create'),
    path('update/<slug:slug>/', views.update_quiz, name='update'),
    path('delete/<slug:slug>/', views.DeleteQuizView.as_view(), name='delete'),
]
