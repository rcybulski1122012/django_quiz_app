from django.urls import path

from quizzes import views

app_name = "quizzes"

urlpatterns = [
    path("create/", views.CreateQuizWithQuestionsView.as_view(), name="create"),
    path(
        "update/<slug:slug>/",
        views.UpdateQuizWithQuestionsView.as_view(),
        name="update",
    ),
    path("delete/<slug:slug>/", views.DeleteQuizView.as_view(), name="delete"),
    path("take/<slug:slug>/", views.TakeQuizView.as_view(), name="take"),
    path("list/", views.QuizzesListView.as_view(), name="list"),
    path("detail/<slug:slug>/", views.QuizDetailView.as_view(), name="detail"),
    path("like/<slug:slug>/", views.like_quiz_view, name="like"),
]
