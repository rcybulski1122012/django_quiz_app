from os import path
from shutil import rmtree

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from quizzes.models import Category, Quiz, Question, Answer
from quizzes.forms import SAME_QUIZ_TITLE_ERROR, ALL_ANSWERS_INCORRECT_ERROR
from quizzes.tests.utils import FormSetTestMixin


class TestCreateQuizView(FormSetTestMixin, TestCase):
    create_quiz_url = reverse('quizzes:create')
    login_url = reverse('accounts:login')
    profile_url = reverse('accounts:profile')

    dummy_media_files_dir = settings.BASE_DIR / 'quizzes' / 'tests' / 'test_media'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')
        cls.category = Category.objects.create(title='none')

    def setUp(self):
        self.client.login(username='User123', password='SecretPass123')

    def create_quiz_with_one_question(self, title='Quiz title', description='Quiz description', category=None,
                                      thumbnail='', question_body='Question body', answer_a='A', answer_b='B',
                                      answer_c='C', answer_d='D', follow=False, answer_d_is_correct='on'):
        category = category or self.category.id

        # Always fourth answer is correct!
        data = {'title': title, 'description': description, 'category': category,
                'thumbnail': thumbnail, 'questions-0-question': question_body,
                'questions-0-answers-0-answer': answer_a, 'questions-0-answers-1-answer': answer_b,
                'questions-0-answers-2-answer': answer_c, 'questions-0-answers-3-answer': answer_d,
                'questions-0-answers-0-is_correct': '', 'questions-0-answers-1-is_correct': '',
                'questions-0-answers-2-is_correct': '', 'questions-0-answers-3-is_correct': answer_d_is_correct,
                'questions-TOTAL_FORMS': 1, 'questions-INITIAL_FORMS': 0, 'questions-0-answers-TOTAL_FORMS': 4,
                'questions-0-answers-INITIAL_FORMS': 0
                }

        return self.client.post(f'{self.create_quiz_url}?questions=1', data=data,
                                follow=follow)

    def test_redirects_to_login_page_when_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.create_quiz_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.create_quiz_url}')

    def test_status_code_is_equal_to_200_when_request_method_is_get(self):
        response = self.client.get(self.create_quiz_url)
        self.assertEqual(response.status_code, 200)

    def test_renders_10_questions_forms_when_questions_number_is_not_given(self):
        response = self.client.get(self.create_quiz_url)
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 10)

    def test_renders_10_questions_forms_when_questions_number_is_not_int(self):
        response = self.client.get(f'{self.create_quiz_url}?questions=not-int')
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 10)

    def test_renders_20_questions_forms_when_questions_number_is_greater_than_20(self):
        response = self.client.get(f'{self.create_quiz_url}?questions=25')
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 20)

    def test_renders_10_question_forms_when_questions_number_is_smaller_than_1(self):
        response = self.client.get(f'{self.create_quiz_url}?questions=-5')
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 10)

    def test_creates_quiz_questions_and_answers_when_given_data_is_correct(self):
        self.create_quiz_with_one_question()
        self.assertTrue(Quiz.objects.filter(title='Quiz title').exists())
        quiz = Quiz.objects.get(title='Quiz title')
        self.assertTrue(quiz.questions.exists())
        self.assertTrue(quiz.questions.all()[0].answers.exists())

    def test_redirects_to_profile_page_when_quiz_is_created_successfully(self):
        response = self.create_quiz_with_one_question(follow=True)
        self.assertRedirects(response, self.profile_url)

    def test_displays_success_message_when_quiz_is_created_successfully(self):
        response = self.create_quiz_with_one_question(follow=True)
        self.assertContains(response, 'Your quiz has been created successfully')

    def test_does_not_create_quiz_when_given_data_is_incorrect(self):
        self.create_quiz_with_one_question(question_body='')
        # It will cause the error, because question body is required
        self.assertFalse(Quiz.objects.filter(title='Quiz title').exists())

    def test_displays_error_message_when_question_body_is_empty(self):
        response = self.create_quiz_with_one_question(question_body='')
        self.assertContains(response, 'This field is required.')

    def test_displays_error_message_when_answer_is_empty(self):
        response = self.create_quiz_with_one_question(answer_a='')
        self.assertContains(response, 'This field is required.')

    def test_displays_error_message_when_any_is_correct_checkbox_is_not_checked(self):
        response = self.create_quiz_with_one_question(answer_d_is_correct='')
        self.assertContains(response, ALL_ANSWERS_INCORRECT_ERROR)

    def test_displays_error_message_when_quiz_with_the_same_title_already_exists(self):
        self.create_quiz_with_one_question()
        response = self.create_quiz_with_one_question()
        self.assertContains(response, SAME_QUIZ_TITLE_ERROR)

    @override_settings(MEDIA_ROOT=dummy_media_files_dir)
    def test_saves_thumbnail(self):
        with open(settings.BASE_DIR / 'media' / 'default-quiz.jpg', 'rb') as img:
            self.create_quiz_with_one_question(thumbnail=img)

        try:
            self.assertTrue(path.exists(path.join(self.dummy_media_files_dir, 'quiz_thumbnails', 'default-quiz.jpg')))
        finally:
            rmtree(self.dummy_media_files_dir)


class TestUpdateQuizView(FormSetTestMixin, TestCase):
    login_url = reverse('accounts:login')
    profile_url = reverse('accounts:profile')

    @staticmethod
    def get_update_quiz_url(slug, questions=None):
        url = reverse('quizzes:update', args=[slug])
        if questions is None:
            return url
        else:
            return f'{url}?questions={questions}'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = Category.objects.create(title='Category')
        cls.user = User.objects.create_user('User123', 'addressemail123@gmail.com', 'SecretPass123')

    def setUp(self):
        self.quiz = Quiz.objects.create(title='Title', category=self.category, author=self.user)
        self.question = Question.objects.create(question='Question', quiz=self.quiz)
        self.question.answers.add(Answer(answer='A', is_correct=False), bulk=False)
        self.question.answers.add(Answer(answer='B', is_correct=False), bulk=False)
        self.question.answers.add(Answer(answer='C', is_correct=False), bulk=False)
        self.question.answers.add(Answer(answer='D', is_correct=True), bulk=False)

        self.client.login(username='User123', password='SecretPass123')

    @staticmethod
    def get_example_form_data(quiz, title='New title', description='New description', category=None,
                              thumbnail=''):
        category = quiz.category.pk or category
        number_of_questions = quiz.questions.count()
        data = {'title': title, 'description': description, 'category': category, 'thumbnail': thumbnail,
                'questions-TOTAL_FORMS': number_of_questions, 'questions-INITIAL_FORMS': number_of_questions}

        for i, question in enumerate(quiz.questions.all()):
            data.update({f'questions-{i}-question': 'New Question', f'questions-{i}-quiz': quiz.pk,
                         f'questions-{i}-id': question.pk,
                         f'questions-{i}-answers-TOTAL_FORMS': '4', f'questions-{i}-answers-INITIAL_FORMS': '4',
                         f'questions-{i}-answers-0-answer': 'New A',
                         f'questions-{i}-answers-0-id': question.answers.all()[0].pk,
                         f'questions-{i}-answers-0-question': question.pk,
                         f'questions-{i}-answers-1-answer': 'New B',
                         f'questions-{i}-answers-1-id': question.answers.all()[1].pk,
                         f'questions-{i}-answers-1-question': question.pk,
                         f'questions-{i}-answers-2-answer': 'New C',
                         f'questions-{i}-answers-2-id': question.answers.all()[2].pk,
                         f'questions-{i}-answers-2-question': question.pk,
                         f'questions-{i}-answers-3-answer': 'New D',
                         f'questions-{i}-answers-3-id': question.answers.all()[2].pk,
                         f'questions-{i}-answers-3-question': question.pk,
                         f'questions-{i}-answers-3-is_correct': 'on'    # Always fourth answers is correct
                         })
        return data

    def add_questions_to_quiz(self, n):
        for i in range(n):
            question = Question.objects.create(question=f'Question{i}', quiz=self.quiz)
            question.answers.add(Answer(answer='A', is_correct=False), bulk=False)
            question.answers.add(Answer(answer='B', is_correct=False), bulk=False)
            question.answers.add(Answer(answer='C', is_correct=False), bulk=False)
            question.answers.add(Answer(answer='D', is_correct=True), bulk=False)

    def test_redirects_to_login_page_when_user_is_not_logged(self):
        update_quiz_url = self.get_update_quiz_url('title')
        self.client.logout()
        response = self.client.get(update_quiz_url, follow=True)

        self.assertRedirects(response, f'{self.login_url}?next={update_quiz_url}')

    def test_returns_403_when_not_author_is_trying_to_update_quiz(self):
        self.client.logout()
        User.objects.create_user('User124', 'addressemail124@gmail.com', 'SecretPass123')
        self.client.login(username='User124', password='SecretPass123')

        response = self.client.get(self.get_update_quiz_url('title'))
        self.assertEqual(response.status_code, 403)

    def test_updates_quiz_when_data_is_correct(self):
        data = self.get_example_form_data(self.quiz)
        self.client.post(self.get_update_quiz_url('title'), data=data, follow=True)
        self.quiz.refresh_from_db()
        self.question.refresh_from_db()
        self.assertEqual(self.quiz.title, 'New title')
        self.assertTrue(self.quiz.questions.filter(question='New Question').exists())
        self.assertTrue(self.question.answers.filter(answer='New A').exists())

    def test_redirects_to_profile_page_when_quiz_is_updated_successfully(self):
        data = self.get_example_form_data(self.quiz)
        response = self.client.post(self.get_update_quiz_url('title'), data=data, follow=True)
        self.assertRedirects(response, self.profile_url)

    def test_displays_success_message_when_quiz_is_updated_successfully(self):
        data = self.get_example_form_data(self.quiz)
        response = self.client.post(self.get_update_quiz_url('title'), data=data, follow=True)
        self.assertContains(response, 'Your quiz has been updated successfully')

    def test_does_not_create_quiz_when_given_data_is_incorrect(self):
        data = self.get_example_form_data(self.quiz)
        data['questions-0-answers-3-is_correct'] = ''
        self.client.post(self.get_update_quiz_url('title'), data=data)
        self.quiz.refresh_from_db()
        self.assertNotEqual(self.quiz.title, 'New title')

    def test_displays_error_message_when_question_body_is_empty(self):
        data = self.get_example_form_data(self.quiz)
        data['questions-0-question'] = ''
        response = self.client.post(self.get_update_quiz_url('title'), data=data)
        self.assertContains(response, 'This field is required.')

    def test_displays_error_message_when_answer_is_empty(self):
        data = self.get_example_form_data(self.quiz)
        data['questions-0-answers-0-answer'] = ''
        response = self.client.post(self.get_update_quiz_url('title'), data=data)
        self.assertContains(response, 'This field is required.')

    def test_displays_error_message_when_any_is_correct_checkbox_is_not_checked(self):
        data = self.get_example_form_data(self.quiz)
        data['questions-0-answers-3-is_correct'] = ''
        response = self.client.post(self.get_update_quiz_url('title'), data=data)
        self.assertContains(response, ALL_ANSWERS_INCORRECT_ERROR)

    def test_displays_error_message_when_quiz_with_the_same_title_already_exists(self):
        Quiz.objects.create(title='title1', category=self.category, author=self.user)
        data = self.get_example_form_data(self.quiz, title='title1')
        response = self.client.post(self.get_update_quiz_url('title'), data=data)
        self.assertContains(response, SAME_QUIZ_TITLE_ERROR)

    def test_display_default_quantity_of_question_forms_when_number_of_questions_is_smaller(self):
        response = self.client.get(self.get_update_quiz_url('title'))
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 10)

    def test_displays_given_quantity_of_questions_forms_when_it_is_greater_than_number_of_questions(self):
        response = self.client.get(self.get_update_quiz_url('title', questions=12))
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 12)

    def test_displays_maximum_quantity_of_question_forms_when_given_number_is_greater_than_max(self):
        response = self.client.get(self.get_update_quiz_url('title', questions=25))
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 20)

    def test_displays_default_quantity_of_question_forms_when_given_number_is_smaller_than_min(self):
        response = self.client.get(self.get_update_quiz_url('title', questions=-5))
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 10)

    def test_displays_default_quantity_of_question_forms_when_given_value_is_not_number(self):
        response = self.client.get(self.get_update_quiz_url('title', questions='not-int'))
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 10)

    def test_displays_the_same_quantity_of_forms_as_questions_when_number_of_questions_is_greater_than_10(self):
        self.add_questions_to_quiz(n=11)
        response = self.client.get(self.get_update_quiz_url('title'))
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 12)

    def test_displays_the_quantity_of_forms_as_questions_when_given_number_of_questions_is_smaller(self):
        self.add_questions_to_quiz(n=11)
        response = self.client.get(self.get_update_quiz_url('title', questions=5))
        self.assertFormsetNumberOfFormsEqual(response.context['questions_formset'], 12)

    def test_deletes_question(self):
        self.add_questions_to_quiz(n=1)
        self.quiz.refresh_from_db()
        data = self.get_example_form_data(self.quiz)
        data['questions-0-DELETE'] = 'on'
        self.client.post(reverse('quizzes:update', args=['title']), data=data)
        self.assertEqual(Question.objects.filter(quiz=self.quiz).count(), 1)

    def test_deletes_quiz_when_last_questions_is_deleted(self):
        data = {**self.get_example_form_data(self.quiz), 'questions-0-DELETE': 'on'}
        self.client.post(reverse('quizzes:update', args=['title']), data=data)
        self.assertFalse(Quiz.objects.filter(title='Title').exists())

