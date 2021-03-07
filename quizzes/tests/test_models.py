import datetime
from unittest.mock import Mock

from django.test import TestCase

from quizzes.models import Answer, Category, Question, Quiz, Score
from quizzes.tests.utils import QuizzesUtilsMixin


class TestCategory(TestCase):
    def test_str(self):
        category = Category(title="title")
        self.assertEqual(str(category), "title")


class TestQuiz(QuizzesUtilsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.create_user()
        cls.category = cls.create_category()

    def setUp(self):
        self.quiz = self.create_quiz()

    def test_str(self):
        self.assertEqual(str(self.quiz), self.QUIZ_TITLE)

    def test_repr(self):
        self.assertEqual(repr(self.quiz), f"<Quiz: {self.QUIZ_TITLE}>")

    def test_slugify_title(self):
        self.assertEqual(self.quiz.slug, self.QUIZ_SLUG)

    def test_get_absolute_url(self):
        expected_url = f"/quizzes/detail/{self.QUIZ_SLUG}/"
        self.assertEqual(self.quiz.get_absolute_url(), expected_url)

    def test_get_average_score_when_no_scores(self):
        avg_score = self.quiz.get_average_score()
        self.assertEqual(avg_score, 0)

    def test_get_average_score_when_only_one_score_exists(self):
        Score.objects.create(user=self.user, quiz=self.quiz, percentage=50)
        avg_score = self.quiz.get_average_score()
        self.assertEqual(avg_score, 50)

    def test_get_average_score_with_few_scores(self):
        scores = [0, 5, 10, 30, 47, 30, 50, 95, 98, 100]
        expected = sum(scores) // len(scores)
        for score in scores:
            Score.objects.create(user=self.user, quiz=self.quiz, percentage=score)
        avg_score = self.quiz.get_average_score()
        self.assertEqual(avg_score, expected)

    def test_sort_by_date_created(self):
        older_quiz = Quiz.objects.create(title="older quiz", author=self.user)
        older_quiz.created = datetime.date(2000, 1, 1)
        older_quiz.save()
        expected = [repr(quiz) for quiz in [older_quiz, self.quiz]]
        self.assertQuerysetEqual(Quiz.objects.sort_by_date_created(asc=True), expected)
        self.assertQuerysetEqual(
            Quiz.objects.sort_by_date_created(asc=False), expected[::-1]
        )

    def test_sort_by_avg_score(self):
        quiz1_scores = [10, 50, 60]
        quiz2_scores = [100, 100, 50]
        quiz2 = self.create_quiz(title="quiz2")
        self.create_scores(quiz=self.quiz, user=self.user, scores=quiz1_scores)
        self.create_scores(quiz=quiz2, user=self.user, scores=quiz2_scores)

        expected = [repr(quiz) for quiz in [self.quiz, quiz2]]

        self.assertQuerysetEqual(Quiz.objects.sort_by_avg_score(asc=True), expected)
        self.assertQuerysetEqual(
            Quiz.objects.sort_by_avg_score(asc=False), expected[::-1]
        )

    def test_sort_by_number_of_questions(self):
        # self.quiz has one question
        quiz2 = self.create_quiz(title="quiz2")
        self.create_question(quiz=quiz2)
        self.create_question(quiz=quiz2)

        expected = [repr(quiz) for quiz in [self.quiz, quiz2]]
        self.assertQuerysetEqual(
            Quiz.objects.sort_by_number_of_questions(asc=True), expected
        )
        self.assertQuerysetEqual(
            Quiz.objects.sort_by_number_of_questions(asc=False), expected[::-1]
        )

    def test_sort_by_number_of_likes(self):
        quiz2 = self.create_quiz(title="quiz2")
        self.quiz.likes = 5
        self.quiz.save()

        expected = [repr(quiz) for quiz in [self.quiz, quiz2]]
        self.assertQuerysetEqual(
            Quiz.objects.sort_by_number_of_likes(asc=True), expected[::-1]
        )
        self.assertQuerysetEqual(
            Quiz.objects.sort_by_number_of_likes(asc=False), expected
        )

    def test_like(self):
        quiz_likes = self.quiz.likes
        fake_session = {}
        self.quiz.like(fake_session)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.likes, quiz_likes + 1)
        self.assertTrue(fake_session[self.quiz.get_session_like_str()])

    def test_is_liked(self):
        fake_session = {}
        self.assertFalse(self.quiz.is_liked(fake_session))
        fake_session[self.quiz.get_session_like_str()] = True
        self.assertTrue(self.quiz.is_liked(fake_session))


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
