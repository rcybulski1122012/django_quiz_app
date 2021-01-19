from django.conf import settings
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Quiz(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quizzes')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='quizzes', null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    question = models.TextField(max_length=300)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.question


class Answer(models.Model):
    answer = models.CharField(max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField()

    def __str__(self):
        return self.answer
