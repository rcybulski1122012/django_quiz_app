from os import path
from shutil import rmtree

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from quizzes.models import Category, Quiz


class TestCreateQuizView(TestCase):
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
                                      answer_c='C', answer_d='D', follow=False, id_d_answer_correct='on'):
        category = category or self.category.id

        # Always fourth answer is correct!
        data = {'title': title, 'description': description, 'category': category,
                'thumbnail': thumbnail, 'questions-0-question': question_body,
                'questions-0-answers-0-answer': answer_a, 'questions-0-answers-1-answer': answer_b,
                'questions-0-answers-2-answer': answer_c, 'questions-0-answers-3-answer': answer_d,
                'questions-0-answers-0-is_correct': '', 'questions-0-answers-1-is_correct': '',
                'questions-0-answers-2-is_correct': '', 'questions-0-answers-3-is_correct': id_d_answer_correct,
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
        self.assertEqual(response.context['question_formset'].extra, 10)

    def test_renders_10_questions_forms_when_questions_number_is_not_int(self):
        response = self.client.get(f'{self.create_quiz_url}?questions=not-int')
        self.assertEqual(response.context['question_formset'].extra, 10)

    def test_renders_20_questions_forms_when_questions_number_is_greater_than_20(self):
        response = self.client.get(f'{self.create_quiz_url}?questions=25')
        self.assertEqual(response.context['question_formset'].extra, 20)

    def test_renders_10_question_forms_when_questions_number_is_less_than_1(self):
        response = self.client.get(f'{self.create_quiz_url}?questions=-5')
        self.assertEqual(response.context['question_formset'].extra, 10)

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
        self.assertContains(response, "Any question can&#x27;t be empty!")

    def test_displays_error_message_when_answers_are_empty(self):
        response = self.create_quiz_with_one_question(answer_a='', answer_b='', answer_c='', answer_d='',
                                                      id_d_answer_correct='')
        self.assertContains(response, "Any answer can&#x27;t be empty!")

    def test_displays_error_message_when_any_is_correct_checkbox_is_not_checked(self):
        response = self.create_quiz_with_one_question(id_d_answer_correct='')
        self.assertContains(response, 'At least one of the answers must be marked as correct!')

    def test_displays_error_message_when_quiz_with_the_same_title_already_exists(self):
        self.create_quiz_with_one_question()
        response = self.create_quiz_with_one_question()
        self.assertContains(response, 'Quiz with the same title already exists!')

    @override_settings(MEDIA_ROOT=dummy_media_files_dir)
    def test_saves_thumbnail(self):
        with open(settings.BASE_DIR / 'media' / 'default-quiz.jpg', 'rb') as img:
            self.create_quiz_with_one_question(thumbnail=img)

        try:
            self.assertTrue(path.exists(path.join(self.dummy_media_files_dir, 'quiz_thumbnails', 'default-quiz.jpg')))
        finally:
            rmtree(self.dummy_media_files_dir)
