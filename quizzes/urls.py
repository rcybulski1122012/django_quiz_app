from django.urls import path
from quizzes import views

app_name = 'quizzes'

urlpatterns = [
    path('create/', views.create_quiz, name='create'),
    path('update/<slug:slug>/', views.update_quiz, name='update'),
    path('delete/<slug:slug>/', views.DeleteQuizView.as_view(), name='delete'),
    path('take/<slug:slug>/', views.take_quiz, name='take'),
    path('list/', views.QuizzesListView.as_view(), name='list'),
    path('detail/<slug:slug>/', views.QuizDetailView.as_view(), name='detail'),
]
