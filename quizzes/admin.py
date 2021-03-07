from django.contrib import admin

from quizzes.models import Answer, Category, Question, Quiz


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "thumbnail", "likes"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question", "quiz"]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["answer", "question", "is_correct"]
