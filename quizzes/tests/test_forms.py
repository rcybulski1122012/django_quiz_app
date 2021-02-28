from django.contrib.auth.models import User
from django.forms import formset_factory
from django.test import TestCase

from quizzes.forms import (AnswerFormSet, BaseTakeQuizFormSet, QuizForm,
                           TakeQuestionForm, create_question_formset)
from quizzes.models import Answer, Category, Question, Quiz
from quizzes.tests.utils import QuizzesUtilsMixin

QuestionFormSet = create_question_formset(number_of_questions=1)
UpdateQuestionFormSet = create_question_formset(number_of_questions=1, can_delete=True)


class TestQuizForm(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="test")
        self.user = User.objects.create_user(
            "User123", "addressemail123@gmail.com", "SecretPass123"
        )

    def test_valid_form(self):
        data = {
            "title": "Example",
            "category": str(self.category.pk),
        }
        form = QuizForm(data=data)
        self.assertTrue(form.is_valid())

    def test_is_invalid_when_quiz_with_the_same_title_already_exists(self):
        Quiz.objects.create(title="Example", category=self.category, author=self.user)
        data = {
            "title": "Example",
            "category": str(self.category.pk),
        }
        form = QuizForm(data=data)
        self.assertFalse(form.is_valid())

    def test_saves_quiz_with_given_author(self):
        data = {
            "title": "Example",
            "category": str(self.category.pk),
        }

        form = QuizForm(data=data)
        quiz = form.save(author=self.user, commit=True)
        self.assertIs(quiz.author, self.user)
        self.assertTrue(Quiz.objects.filter(title=quiz.title).exists())

    def test_invalid_when_any_word_of_description_is_longer_than_45_characters(self):
        data = {
            "title": "Example",
            "category": str(self.category.pk),
            "description": "one_very_long_word_and_that_should_raise_a_validation_error",
        }
        form = QuizForm(data)
        self.assertFalse(form.is_valid())


class TestAnswerFormSet(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Category")
        self.user = User.objects.create_user(
            "User123", "addressemail123@gmail.com", "SecretPass123"
        )
        self.quiz = Quiz.objects.create(
            title="Title", category=self.category, author=self.user
        )
        self.question = Question.objects.create(question="Question", quiz=self.quiz)

    @staticmethod
    def get_example_formset_data(
        answer_a="A", answer_b="B", answer_c="C", answer_d="D", answer_d_is_correct="on"
    ):
        return {
            "answers-0-answer": answer_a,
            "answers-0-is_correct": "",
            "answers-1-answer": answer_b,
            "answers-1-is_correct": "",
            "answers-2-answer": answer_c,
            "answers-2-is_correct": "",
            "answers-3-answer": answer_d,
            "answers-3-is_correct": answer_d_is_correct,
            "answers-TOTAL_FORMS": 4,
            "answers-INITIAL_FORMS": 0,
        }

    def test_valid_formset(self):
        data = self.get_example_formset_data()
        formset = AnswerFormSet(data=data)
        self.assertTrue(formset.is_valid())

    def test_is_invalid_when_answers_are_empty(self):
        data = self.get_example_formset_data(
            answer_a="", answer_b="", answer_c="", answer_d=""
        )
        formset = AnswerFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_is_invalid_when_all_is_correct_options_are_empty(self):
        data = self.get_example_formset_data(answer_d_is_correct="")
        formset = AnswerFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_save(self):
        data = self.get_example_formset_data()
        formset = AnswerFormSet(data=data, instance=self.question)
        formset.save()
        self.assertTrue(Answer.objects.filter(question=self.question).exists())


class TestQuestionFormSet(QuizzesUtilsMixin, TestCase):
    @staticmethod
    def get_example_formset_data(
        title="Quiz title",
        description="Quiz description",
        category=None,
        thumbnail="",
        question_body="Question body",
        answer_a="A",
        answer_b="B",
        answer_c="C",
        answer_d="D",
        answer_d_is_correct="on",
    ):
        return {
            "title": title,
            "description": description,
            "category": category,
            "thumbnail": thumbnail,
            "questions-0-question": question_body,
            "questions-0-answers-0-answer": answer_a,
            "questions-0-answers-1-answer": answer_b,
            "questions-0-answers-2-answer": answer_c,
            "questions-0-answers-3-answer": answer_d,
            "questions-0-answers-0-is_correct": "",
            "questions-0-answers-1-is_correct": "",
            "questions-0-answers-2-is_correct": "",
            "questions-0-answers-3-is_correct": answer_d_is_correct,
            "questions-TOTAL_FORMS": 1,
            "questions-INITIAL_FORMS": 0,
            "questions-0-answers-TOTAL_FORMS": 4,
            "questions-0-answers-INITIAL_FORMS": 0,
        }

    def test_valid(self):
        data = self.get_example_formset_data()
        formset = QuestionFormSet(data=data)
        self.assertTrue(formset.is_valid())

    def test_invalid_when_any_question_is_empty(self):
        data = self.get_example_formset_data(question_body="")
        formset = QuestionFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_invalid_when_answer_form_is_invalid(self):
        data = self.get_example_formset_data(answer_a="")
        formset = QuestionFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_form_has_AnswerFormSet(self):
        formset = QuestionFormSet()
        self.assertTrue(isinstance(formset.forms[0].nested, AnswerFormSet))

    def test_saves_questions_and_answers(self):
        category = self.create_category()
        user = self.create_user()
        quiz = self.create_quiz(user=user, category=category)

        data = self.get_example_formset_data()
        formset = QuestionFormSet(data=data, instance=quiz)
        questions = formset.save()
        self.assertTrue(Question.objects.filter(quiz=quiz).exists())
        self.assertTrue(Answer.objects.filter(question=questions[0]).exists())

    def test_invalid_when_any_word_of_question_body_is_longer_than_45_characters(self):
        data = self.get_example_formset_data(
            question_body="one_very_long_word_and_that_should_raise_a_validation_error"
        )
        formset = QuestionFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_invalid_when_delete_all_questions(self):
        category = self.create_category()
        user = self.create_user()
        quiz = self.create_quiz(user=user, category=category)
        self.create_question(quiz)

        data = self.get_example_formset_data()
        data["questions-0-DELETE"] = "on"
        formset = UpdateQuestionFormSet(data=data, instance=quiz)
        self.assertFalse(formset.is_valid())


class TestTakeQuizFormSet(QuizzesUtilsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.create_category()
        cls.user = cls.create_user()

    def setUp(self):
        self.quiz = self.create_quiz()
        self.question = self.create_question()
        self.TakeQuizFormset = formset_factory(
            TakeQuestionForm,
            extra=self.question.answers.count(),
            formset=BaseTakeQuizFormSet,
        )

    def get_formset_data(self, is_correct=True):
        answer_index = 3 if is_correct else 0  # D answer is correct
        data = {
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-0-answer": self.question.answers.all()[answer_index].pk,
        }
        return data

    def test_get_score_when_answers_are_correct(self):
        formset = self.TakeQuizFormset(quiz=self.quiz, data=self.get_formset_data())
        formset.is_valid()
        score = formset.get_score()
        self.assertEqual(score, 1)

    def test_get_score_when_answers_are_incorrect(self):
        formset = self.TakeQuizFormset(
            quiz=self.quiz, data=self.get_formset_data(is_correct=False)
        )
        formset.is_valid()
        score = formset.get_score()
        self.assertEqual(score, 0)

    def test_get_score_when_answers_are_not_given(self):
        formset = self.TakeQuizFormset(
            quiz=self.quiz, data={"form-TOTAL_FORMS": 1, "form-INITIAL_FORMS": 0}
        )
        formset.is_valid()
        score = formset.get_score()
        self.assertEqual(score, 0)

    def test_questions_labels(self):
        formset = self.TakeQuizFormset(quiz=self.quiz)
        formset.is_valid()
        formset_labels = {
            label for form in formset.forms if (label := form.fields["answer"].label)
        }
        questions_titles = {question.question for question in self.quiz.questions.all()}
        self.assertEqual(formset_labels, questions_titles)
