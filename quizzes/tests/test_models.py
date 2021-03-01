from django.test import TestCase

from quizzes.models import Answer, Category, Question, Quiz, Score
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

    def test_get_average_score_when_no_scores(self):
        quiz = Quiz.objects.create(title="title", author=self.user)
        avg_score = quiz.get_average_score()
        self.assertEqual(avg_score, 0)

    def test_get_average_score_when_only_one_score_exists(self):
        quiz = Quiz.objects.create(title="title", author=self.user)
        Score.objects.create(user=self.user, quiz=quiz, percentage=50)
        avg_score = quiz.get_average_score()
        self.assertEqual(avg_score, 50)

    def test_get_average_score_with_few_scores(self):
        quiz = Quiz.objects.create(title="title", author=self.user)
        scores = [0, 5, 10, 30, 47, 30, 50, 95, 98, 100]
        expected = sum(scores) // len(scores)
        for score in scores:
            Score.objects.create(user=self.user, quiz=quiz, percentage=score)
        avg_score = quiz.get_average_score()
        self.assertEqual(avg_score, expected)


class TestQuestion(TestCase):
    def test_str(self):
        question = Question(question="question")
        self.assertEqual(str(question), "question")


class TestAnswer(TestCase):
    def test_str(self):
        answer = Answer(answer="answer")
        self.assertEqual(str(answer), "answer")


class TestResult(QuizzesUtilsMixin, TestCase):
    def test_str(self):
        category = self.create_category()
        user = self.create_user()
        quiz = self.create_quiz(user=user, category=category)
        score = Score(user=user, quiz=quiz, percentage=10)

        self.assertEqual(str(score), f"{quiz}:{user}-10%")
