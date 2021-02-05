from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Quiz(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quizzes')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='quizzes', null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    thumbnail = models.ImageField(upload_to='quiz_thumbnails/', default='default-quiz.jpg')

    class Meta:
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'<Quiz: {self.title}>'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Question(models.Model):
    question = models.TextField(max_length=300)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.question


class Answer(models.Model):
    answer = models.CharField(max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer
