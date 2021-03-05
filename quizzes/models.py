from django.conf import settings
from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title


class SortQuizzesQuerySet(models.QuerySet):
    def sort_by_date_created(self, asc):
        return super().order_by("created" if asc else "-created")

    def sort_by_avg_score(self, asc):
        return (
            super()
            .annotate(avg_score=Avg("scores__percentage"))
            .order_by("avg_score" if asc else "-avg_score")
        )

    def sort_by_number_of_questions(self, asc):
        return (
            super()
            .annotate(number_of_questions=Count("questions"))
            .order_by("number_of_questions" if asc else "-number_of_questions")
        )


class Quiz(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name="quizzes", null=True
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    thumbnail = models.ImageField(
        upload_to="quiz_thumbnails/", default="default-quiz.jpg"
    )

    objects = SortQuizzesQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Quiz: {self.title}>"

    def get_absolute_url(self):
        return reverse("quizzes:detail", args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_average_score(self):
        return int(
            self.scores.aggregate(models.Avg("percentage"))["percentage__avg"] or 0
        )


class Question(models.Model):
    question = models.TextField(max_length=300)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return self.question


class Answer(models.Model):
    answer = models.CharField(max_length=100)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer


class Score(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scores"
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="scores")
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quiz}:{self.user}-{self.percentage}%"
