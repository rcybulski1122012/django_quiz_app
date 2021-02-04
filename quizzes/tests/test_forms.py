from django.contrib.auth.models import User
from django.test import TestCase

from quizzes.forms import QuizCreationForm, AnswerFormSet, create_question_formset
from quizzes.models import Category, Quiz, Question, Answer

QuestionFormSet = create_question_formset(number_of_question=1)


class TestQuizCreationForm(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='test')
        self.user = User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')

    def test_valid_form(self):
        data = {
            'title': 'Example',
            'category': str(self.category.pk),
        }
        form = QuizCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_is_invalid_when_quiz_with_the_same_title_already_exists(self):
        Quiz.objects.create(title='Example', category=self.category, author=self.user)
        data = {
            'title': 'Example',
            'category': str(self.category.pk),
        }
        form = QuizCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_saves_quiz_with_given_author(self):
        data = {
            'title': 'Example',
            'category': str(self.category.pk),
        }

        form = QuizCreationForm(data=data)
        quiz = form.save(author=self.user, commit=True)
        self.assertIs(quiz.author, self.user)
        self.assertTrue(Quiz.objects.filter(title=quiz.title).exists())


class TestAnswerFormSet(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Category')
        self.user = User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')
        self.quiz = Quiz.objects.create(title='Title', category=self.category, author=self.user)
        self.question = Question.objects.create(question='Question', quiz=self.quiz)

    @staticmethod
    def get_example_formset_data(answer_a='A', answer_b='B', answer_c='C', answer_d='D',
                                 answer_d_is_correct='on'):
        return {'answers-0-answer': answer_a, 'answers-0-is_correct': '',
                'answers-1-answer': answer_b, 'answers-1-is_correct': '',
                'answers-2-answer': answer_c, 'answers-2-is_correct': '',
                'answers-3-answer': answer_d, 'answers-3-is_correct': answer_d_is_correct,
                'answers-TOTAL_FORMS': 4, 'answers-INITIAL_FORMS': 0}

    def test_valid_formset(self):
        data = self.get_example_formset_data()
        formset = AnswerFormSet(data=data)
        self.assertTrue(formset.is_valid())

    def test_is_invalid_when_answers_are_empty(self):
        data = self.get_example_formset_data(answer_a='', answer_b='', answer_c='', answer_d='')
        formset = AnswerFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_is_invalid_when_all_is_correct_options_are_empty(self):
        data = self.get_example_formset_data(answer_d_is_correct='')
        formset = AnswerFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_save(self):
        data = self.get_example_formset_data()
        formset = AnswerFormSet(data=data, instance=self.question)
        formset.save()
        self.assertTrue(Answer.objects.filter(question=self.question).exists())


class TestQuestionFormSet(TestCase):
    @staticmethod
    def get_example_formset_data(title='Quiz title', description='Quiz description', category=None,
                                 thumbnail='', question_body='Question body', answer_a='A', answer_b='B',
                                 answer_c='C', answer_d='D', answer_d_is_correct='on'):
        return {'title': title, 'description': description, 'category': category,
                'thumbnail': thumbnail, 'questions-0-question': question_body,
                'questions-0-answers-0-answer': answer_a, 'questions-0-answers-1-answer': answer_b,
                'questions-0-answers-2-answer': answer_c, 'questions-0-answers-3-answer': answer_d,
                'questions-0-answers-0-is_correct': '', 'questions-0-answers-1-is_correct': '',
                'questions-0-answers-2-is_correct': '', 'questions-0-answers-3-is_correct': answer_d_is_correct,
                'questions-TOTAL_FORMS': 1, 'questions-INITIAL_FORMS': 0, 'questions-0-answers-TOTAL_FORMS': 4,
                'questions-0-answers-INITIAL_FORMS': 0}

    def test_valid(self):
        data = self.get_example_formset_data()
        formset = QuestionFormSet(data=data)
        self.assertTrue(formset.is_valid())

    def test_invalid_when_any_question_is_empty(self):
        data = self.get_example_formset_data(question_body='')
        formset = QuestionFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_invalid_when_answer_form_is_invalid(self):
        data = self.get_example_formset_data(answer_a='')
        formset = QuestionFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_form_has_AnswerFormSet(self):
        formset = QuestionFormSet()
        self.assertTrue(isinstance(formset.forms[0].nested, AnswerFormSet))

    def test_saves_questions_and_answers(self):
        category = Category.objects.create(title='Category')
        user = User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')
        quiz = Quiz.objects.create(title='Title', category=category, author=user)

        data = self.get_example_formset_data()
        formset = QuestionFormSet(data=data, instance=quiz)
        questions = formset.save()
        self.assertTrue(Question.objects.filter(quiz=quiz).exists())
        self.assertTrue(Answer.objects.filter(question=questions[0]).exists())
