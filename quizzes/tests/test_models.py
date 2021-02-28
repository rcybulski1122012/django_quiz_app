from django.test import TestCase

from quizzes.models import Answer, Category, Question, Quiz
from quizzes.tests.utils import QuizzesUtilsMixin


class TestCategory(TestCase):
    def test_str(self):
        category = Category(title="title")
        self.assertEqual(str(category), "title")

    def test_slugify_title(self):
        category = Category.objects.create(title="category title")
        self.assertEqual(category.slug, "category-title")


class TestQuiz(QuizzesUtilsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.create_user()

    def test_str(self):
        quiz = Quiz(title="title")
        self.assertEqual(str(quiz), "title")

    def test_repr(self):
        quiz = Quiz(title="title")
        self.assertEqual(repr(quiz), "<Quiz: title>")

    def test_slugify_title(self):
        quiz = Quiz.objects.create(title="quiz title", author=self.user)
        self.assertEqual(quiz.slug, "quiz-title")

    def test_get_absolute_url(self):
        quiz = Quiz.objects.create(title="title", author=self.user)
        expected_url = "/quizzes/detail/title/"
        self.assertEqual(quiz.get_absolute_url(), expected_url)


class TestQuestion(TestCase):
    def test_str(self):
        question = Question(question="question")
        self.assertEqual(str(question), "question")


class TestAnswer(TestCase):
    def test_str(self):
        answer = Answer(answer="answer")
        self.assertEqual(str(answer), "answer")
