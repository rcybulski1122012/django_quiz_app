import datetime
from os import path
from shutil import rmtree
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from quizzes.forms import (ALL_ANSWERS_INCORRECT_ERROR,
                           DELETE_ALL_QUESTIONS_ERROR, SAME_QUIZ_TITLE_ERROR,
                           TOO_LONG_WORD_ERROR, FilterSortQuizzesForm)
from quizzes.models import Question, Quiz, Score
from quizzes.tests.utils import FormSetTestMixin, QuizzesUtilsMixin
from quizzes.views import (QUIZ_CREATE_SUCCESS_MESSAGE,
                           QUIZ_DELETE_SUCCESS_MESSAGE,
                           QUIZ_UPDATE_SUCCESS_MESSAGE)


class TestCreateQuizView(QuizzesUtilsMixin, FormSetTestMixin, TestCase):
    dummy_media_files_dir = settings.BASE_DIR / "quizzes" / "tests" / "test_media"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.create_user()
        cls.category = cls.create_category()

    def setUp(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

    def test_redirects_to_login_page_when_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.create_quiz_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.create_quiz_url}")

    def test_status_code_is_equal_to_200_when_request_method_is_get(self):
        response = self.client.get(self.create_quiz_url)
        self.assertEqual(response.status_code, 200)

    def test_renders_10_questions_forms_when_questions_number_is_not_given(self):
        response = self.client.get(self.create_quiz_url)
        self.assertFormsetNumberOfFormsEqual(response.context["questions_formset"], 10)

    def test_renders_10_questions_forms_when_questions_number_is_not_int(self):
        response = self.client.get(f"{self.create_quiz_url}?questions=not-int")
        self.assertFormsetNumberOfFormsEqual(response.context["questions_formset"], 10)

    def test_renders_20_questions_forms_when_questions_number_is_greater_than_20(self):
        response = self.client.get(f"{self.create_quiz_url}?questions=25")
        self.assertFormsetNumberOfFormsEqual(response.context["questions_formset"], 20)

    def test_renders_10_question_forms_when_questions_number_is_smaller_than_1(self):
        response = self.client.get(f"{self.create_quiz_url}?questions=-5")
        self.assertFormsetNumberOfFormsEqual(response.context["questions_formset"], 10)

    def test_creates_quiz_questions_and_answers_when_given_data_is_correct(self):
        self.post_create_view_with_one_question_quiz()
        self.assertTrue(Quiz.objects.filter(title=self.QUIZ_TITLE).exists())
        quiz = Quiz.objects.get()
        self.assertTrue(quiz.questions.exists())
        self.assertTrue(quiz.questions.all()[0].answers.exists())

    def test_redirects_to_profile_page_when_quiz_is_created_successfully(self):
        response = self.post_create_view_with_one_question_quiz(follow=True)
        self.assertRedirects(response, self.profile_url)

    def test_displays_success_message_when_quiz_is_created_successfully(self):
        response = self.post_create_view_with_one_question_quiz(follow=True)
        self.assertContains(response, QUIZ_CREATE_SUCCESS_MESSAGE)

    def test_does_not_create_quiz_when_given_data_is_incorrect(self):
        self.post_create_view_with_one_question_quiz(question_body="")
        # It will cause the error, because question body is required
        self.assertFalse(Quiz.objects.filter(title=self.QUIZ_TITLE).exists())

    def test_displays_error_message_when_question_body_is_empty(self):
        response = self.post_create_view_with_one_question_quiz(question_body="")
        self.assertContains(response, "This field is required.")

    def test_displays_error_message_when_answer_is_empty(self):
        response = self.post_create_view_with_one_question_quiz(answer_a="")
        self.assertContains(response, "This field is required.")

    def test_displays_error_message_when_any_is_correct_checkbox_is_not_checked(self):
        response = self.post_create_view_with_one_question_quiz(answer_d_is_correct="")
        self.assertContains(response, ALL_ANSWERS_INCORRECT_ERROR)

    def test_displays_error_message_when_quiz_with_the_same_title_already_exists(self):
        self.post_create_view_with_one_question_quiz()
        response = self.post_create_view_with_one_question_quiz()
        self.assertContains(response, SAME_QUIZ_TITLE_ERROR)

    @override_settings(MEDIA_ROOT=dummy_media_files_dir)
    def test_saves_thumbnail(self):
        with open(settings.BASE_DIR / "media" / "default-quiz.jpg", "rb") as img:
            self.post_create_view_with_one_question_quiz(thumbnail=img)

        try:
            self.assertTrue(
                path.exists(
                    path.join(
                        self.dummy_media_files_dir,
                        "quiz_thumbnails",
                        "default-quiz.jpg",
                    )
                )
            )
        finally:
            rmtree(self.dummy_media_files_dir)

    def test_displays_error_when_any_word_of_description_is_longer_than_45_characters(
        self,
    ):
        response = self.post_create_view_with_one_question_quiz(
            description="one_very_long_word_and_that_should_raise_a_validation_error"
        )
        self.assertContains(response, TOO_LONG_WORD_ERROR)

    def test_displays_error_when_any_word_of_question_body_is_longer_than_45_characters(
        self,
    ):
        response = self.post_create_view_with_one_question_quiz(
            question_body="one_very_long_word_and_that_should_raise_a_validation_error"
        )
        self.assertContains(response, TOO_LONG_WORD_ERROR)


class TestUpdateQuizView(QuizzesUtilsMixin, FormSetTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.create_category()
        cls.user = cls.create_user()

    def setUp(self):
        self.quiz = self.create_quiz()
        self.question = self.create_question()
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

    @staticmethod
    def get_example_update_quiz_form_data(
        quiz,
        title="New title",
        description="New description",
        category=None,
        thumbnail="",
    ):
        category = quiz.category.pk or category
        number_of_questions = quiz.questions.count()
        data = {
            "title": title,
            "description": description,
            "category": category,
            "thumbnail": thumbnail,
            "questions-TOTAL_FORMS": number_of_questions,
            "questions-INITIAL_FORMS": number_of_questions,
        }

        for i, question in enumerate(quiz.questions.all()):
            data.update(
                {
                    f"questions-{i}-question": "New Question",
                    f"questions-{i}-quiz": quiz.pk,
                    f"questions-{i}-id": question.pk,
                    f"questions-{i}-answers-TOTAL_FORMS": "4",
                    f"questions-{i}-answers-INITIAL_FORMS": "4",
                    f"questions-{i}-answers-0-answer": "New A",
                    f"questions-{i}-answers-0-id": question.answers.all()[0].pk,
                    f"questions-{i}-answers-0-question": question.pk,
                    f"questions-{i}-answers-1-answer": "New B",
                    f"questions-{i}-answers-1-id": question.answers.all()[1].pk,
                    f"questions-{i}-answers-1-question": question.pk,
                    f"questions-{i}-answers-2-answer": "New C",
                    f"questions-{i}-answers-2-id": question.answers.all()[2].pk,
                    f"questions-{i}-answers-2-question": question.pk,
                    f"questions-{i}-answers-3-answer": "New D",
                    f"questions-{i}-answers-3-id": question.answers.all()[2].pk,
                    f"questions-{i}-answers-3-question": question.pk,
                    f"questions-{i}-answers-3-is_correct": "on",  # Always fourth answers is correct
                }
            )
        return data

    def test_redirects_to_login_page_when_user_is_not_logged(self):
        update_quiz_url = self.get_update_quiz_url(self.QUIZ_SLUG)
        self.client.logout()
        response = self.client.get(self.get_update_quiz_url(self.QUIZ_SLUG))

        self.assertRedirects(response, f"{self.login_url}?next={update_quiz_url}")

    def test_returns_404_when_quiz_with_given_slug_does_not_exists(self):
        response = self.client.get(self.get_update_quiz_url("does-not-exist"))
        self.assertEqual(response.status_code, 404)

    def test_returns_403_when_not_author_is_trying_to_update_quiz(self):
        self.client.logout()
        User.objects.create_user(
            "User124", "addressemail124@gmail.com", "SecretPass123"
        )
        self.client.login(username="User124", password="SecretPass123")

        response = self.client.get(self.get_update_quiz_url(self.QUIZ_SLUG))
        self.assertEqual(response.status_code, 403)

    def test_updates_quiz_when_data_is_correct(self):
        data = self.get_example_update_quiz_form_data(self.quiz)
        self.client.post(
            self.get_update_quiz_url(self.QUIZ_SLUG), data=data, follow=True
        )
        self.quiz.refresh_from_db()
        self.question.refresh_from_db()
        self.assertEqual(self.quiz.title, "New title")
        self.assertTrue(self.quiz.questions.filter(question="New Question").exists())
        self.assertTrue(self.question.answers.filter(answer="New A").exists())

    def test_redirects_to_profile_page_when_quiz_is_updated_successfully(self):
        data = self.get_example_update_quiz_form_data(self.quiz)
        response = self.client.post(
            self.get_update_quiz_url(self.QUIZ_SLUG), data=data, follow=True
        )
        self.assertRedirects(response, self.profile_url)

    def test_displays_success_message_when_quiz_is_updated_successfully(self):
        data = self.get_example_update_quiz_form_data(self.quiz)
        response = self.client.post(
            self.get_update_quiz_url(self.QUIZ_SLUG), data=data, follow=True
        )
        self.assertContains(response, QUIZ_UPDATE_SUCCESS_MESSAGE)

    def test_does_not_create_quiz_when_given_data_is_incorrect(self):
        data = self.get_example_update_quiz_form_data(self.quiz)
        data["questions-0-answers-3-is_correct"] = ""
        self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.quiz.refresh_from_db()
        self.assertNotEqual(self.quiz.title, "New title")

    def test_displays_error_message_when_question_body_is_empty(self):
        data = self.get_example_update_quiz_form_data(self.quiz)
        data["questions-0-question"] = ""
        response = self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertContains(response, "This field is required.")

    def test_displays_error_message_when_answer_is_empty(self):
        data = self.get_example_update_quiz_form_data(self.quiz)
        data["questions-0-answers-0-answer"] = ""
        response = self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertContains(response, "This field is required.")

    def test_displays_error_message_when_any_is_correct_checkbox_is_not_checked(self):
        data = self.get_example_update_quiz_form_data(self.quiz)
        data["questions-0-answers-3-is_correct"] = ""
        response = self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertContains(response, ALL_ANSWERS_INCORRECT_ERROR)

    def test_displays_error_when_last_questions_is_deleted(self):
        data = self.get_example_update_quiz_form_data(self.quiz)
        data["questions-0-DELETE"] = "on"
        response = self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertContains(response, DELETE_ALL_QUESTIONS_ERROR)

    def test_displays_error_when_any_word_of_description_is_longer_than_45_characters(
        self,
    ):
        data = self.get_example_update_quiz_form_data(self.quiz)
        data[
            "description"
        ] = "one_very_long_word_and_that_should_raise_a_validation_error"
        response = self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertContains(response, TOO_LONG_WORD_ERROR)

    def test_displays_error_when_any_word_of_question_body_is_longer_than_45_characters(
        self,
    ):
        data = self.get_example_update_quiz_form_data(self.quiz)
        data[
            "questions-0-question"
        ] = "one_very_long_word_and_that_should_raise_a_validation_error"
        response = self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertContains(response, TOO_LONG_WORD_ERROR)

    def test_displays_error_message_when_quiz_with_the_same_title_already_exists(self):
        Quiz.objects.create(title="title1", category=self.category, author=self.user)
        data = self.get_example_update_quiz_form_data(self.quiz, title="title1")
        response = self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertContains(response, SAME_QUIZ_TITLE_ERROR)

    def test_renders_the_same_number_of_forms_as_quiz_questions_when_number_is_not_given(
        self,
    ):
        response = self.client.get(self.get_update_quiz_url(self.QUIZ_SLUG))
        number_of_questions = self.quiz.questions.count()
        self.assertFormsetNumberOfFormsEqual(
            response.context["questions_formset"], number_of_questions
        )

    def test_renders_the_same_number_of_forms_as_quiz_questions_when_given_number_is_smaller(
        self,
    ):
        self.create_question(quiz=self.quiz)
        response = self.client.get(
            self.get_update_quiz_url(self.QUIZ_SLUG, questions=1)
        )
        number_of_questions = self.quiz.questions.count()
        self.assertFormsetNumberOfFormsEqual(
            response.context["questions_formset"], number_of_questions
        )

    def test_renders_given_quantity_of_questions_forms_when_it_is_greater_than_number_of_quiz_questions(
        self,
    ):
        response = self.client.get(
            self.get_update_quiz_url(self.QUIZ_SLUG, questions=5)
        )
        self.assertFormsetNumberOfFormsEqual(response.context["questions_formset"], 5)

    def test_renders_maximum_quantity_of_question_forms_when_given_number_is_greater_than_max(
        self,
    ):
        response = self.client.get(
            self.get_update_quiz_url(self.QUIZ_SLUG, questions=25)
        )
        self.assertFormsetNumberOfFormsEqual(response.context["questions_formset"], 20)

    def test_renders_the_same_number_of_forms_as_quiz_questions_when_given_number_is_smaller_than_min(
        self,
    ):
        response = self.client.get(
            self.get_update_quiz_url(self.QUIZ_SLUG, questions=-5)
        )
        number_of_questions = self.quiz.questions.count()
        self.assertFormsetNumberOfFormsEqual(
            response.context["questions_formset"], number_of_questions
        )

    def test_renders_the_same_number_of_forms_as_quiz_questions_when_given_value_is_not_number(
        self,
    ):
        response = self.client.get(
            self.get_update_quiz_url(self.QUIZ_SLUG, questions="not-int")
        )
        number_of_questions = self.quiz.questions.count()
        self.assertFormsetNumberOfFormsEqual(
            response.context["questions_formset"], number_of_questions
        )

    def test_deletes_question(self):
        self.add_questions_to_quiz(n=1)
        self.quiz.refresh_from_db()
        data = self.get_example_update_quiz_form_data(self.quiz)
        data["questions-0-DELETE"] = "on"
        self.client.post(self.get_update_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertEqual(Question.objects.filter(quiz=self.quiz).count(), 1)


class TestDeleteQuizView(QuizzesUtilsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.create_category()
        cls.user = cls.create_user()

    def setUp(self):
        self.quiz = self.create_quiz()
        self.question = self.create_question()
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

    def test_returns_404_when_quiz_with_given_slug_does_not_exists(self):
        response = self.client.get(self.get_delete_quiz_url("does-not-exist"))
        self.assertEqual(response.status_code, 404)

    def test_redirects_to_login_page_when_user_is_not_logged(self):
        delete_quiz_url = self.get_delete_quiz_url(self.QUIZ_SLUG)
        self.client.logout()
        response = self.client.get(self.get_delete_quiz_url(slug=self.QUIZ_SLUG))
        self.assertRedirects(response, f"{self.login_url}?next={delete_quiz_url}")

    def test_returns_403_when_not_author_is_trying_to_delete_quiz(self):
        self.client.logout()
        User.objects.create_user(
            "User124", "addressemail124@gmail.com", "SecretPass123"
        )
        self.client.login(username="User124", password="SecretPass123")

        response = self.client.get(self.get_delete_quiz_url(slug=self.QUIZ_SLUG))
        self.assertEqual(response.status_code, 403)

    def test_deletes_quiz(self):
        self.client.post(self.get_delete_quiz_url(self.QUIZ_SLUG))
        self.assertFalse(self.user.quizzes.exists())

    def test_redirects_to_profile_page_when_quiz_is_deleted(self):
        response = self.client.post(self.get_delete_quiz_url(self.QUIZ_SLUG))
        self.assertRedirects(response, self.profile_url)

    def test_displays_success_message_when_quiz_is_deleted(self):
        response = self.client.post(
            self.get_delete_quiz_url(self.QUIZ_SLUG), follow=True
        )
        self.assertContains(response, QUIZ_DELETE_SUCCESS_MESSAGE)


class TestTakeQuizView(QuizzesUtilsMixin, FormSetTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.create_category()
        cls.user = cls.create_user()

    def setUp(self):
        self.quiz = self.create_quiz()
        self.question = self.create_question()
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

    def get_form_data(self, is_correct=True):
        answer_index = 3 if is_correct else 0  # D answer is correct
        data = {
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-0-answer": self.question.answers.all()[answer_index].pk,
        }
        return data

    def test_returns_404_when_quiz_with_given_slug_does_not_exists(self):
        response = self.client.get(self.get_take_quiz_url("does-not-exist"))
        self.assertEqual(response.status_code, 404)

    def test_renders_forms_with_proper_number_of_questions(self):
        response = self.client.get(self.get_take_quiz_url(self.QUIZ_SLUG))
        self.assertFormsetNumberOfFormsEqual(
            response.context["formset"], self.quiz.questions.count()
        )

    def test_displays_score_when_answers_are_correct(self):
        response = self.client.post(
            self.get_take_quiz_url(self.QUIZ_SLUG), data=self.get_form_data()
        )
        self.assertContains(response, "Congratulations! You got 100% (1/1)")

    def test_displays_score_when_answers_are_incorrect(self):
        response = self.client.post(
            self.get_take_quiz_url(self.QUIZ_SLUG),
            data=self.get_form_data(is_correct=False),
        )
        self.assertContains(response, "Congratulations! You got 0% (0/1)")

    def test_display_score_when_answers_are_not_checked(self):
        data = {"form-TOTAL_FORMS": 1, "form-INITIAL_FORMS": 0}
        response = self.client.post(self.get_take_quiz_url(self.QUIZ_SLUG), data=data)
        self.assertContains(response, "Congratulations! You got 0% (0/1)")

    def test_creates_score_if_user_is_logged(self):
        self.client.post(
            self.get_take_quiz_url(self.QUIZ_SLUG), data=self.get_form_data()
        )
        self.assertTrue(Score.objects.filter(user=self.user, quiz=self.quiz).exists())


class TestQuizzesListView(QuizzesUtilsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category1 = cls.create_category(title="Category1")
        cls.category2 = cls.create_category(title="Category2")
        cls.user1 = cls.create_user(username="User1", email="addressemail1@gmail.com")
        cls.user2 = cls.create_user(username="User2", email="addressemail2@gmail.com")

    def setUp(self):
        self.quiz1 = self.create_quiz(
            title="Quiz1", user=self.user1, category=self.category1
        )

        self.quiz2 = self.create_quiz(
            title="Quiz2", user=self.user2, category=self.category2
        )

        self.quiz3 = self.create_quiz(
            title="Quiz3", user=self.user1, category=self.category2
        )

    def test_context_contains_author_username_and_category_slug(self):
        response = self.client.get(
            self.get_list_url(
                author_username=self.user1.username, category_slug=self.category1.slug
            )
        )
        self.assertEqual(response.context["author_username"], self.user1.username)
        self.assertEqual(response.context["category_slug"], self.category1.slug)

    def test_context_contains_FilterQuizzesForm(self):
        response = self.client.get(self.get_list_url())
        form = response.context["sort_filter_form"]
        self.assertTrue(isinstance(form, FilterSortQuizzesForm))

    def test_displays_all_quizzes_when_no_filters(self):
        # Number of quizzes that were created in test case is 3
        # and the pagination of view is 9 so it should display all quizzes
        response = self.client.get(self.get_list_url())
        expected_qs = [repr(quiz) for quiz in Quiz.objects.all()]
        self.assertQuerysetEqual(
            response.context["quizzes"], expected_qs, ordered=False
        )

    def test_filter_by_username(self):
        response = self.client.get(
            self.get_list_url(author_username=self.user1.username)
        )
        expected_qs = [
            repr(quiz)
            for quiz in Quiz.objects.filter(author__username=self.user1.username)
        ]
        self.assertQuerysetEqual(
            response.context["quizzes"], expected_qs, ordered=False
        )

    def test_filter_by_category(self):
        response = self.client.get(self.get_list_url(category_slug=self.category1.slug))
        expected_qs = [
            repr(quiz)
            for quiz in Quiz.objects.filter(category__slug=self.category1.slug)
        ]
        self.assertQuerysetEqual(
            response.context["quizzes"], expected_qs, ordered=False
        )

    def test_both_filters(self):
        response = self.client.get(
            self.get_list_url(
                author_username=self.user1.username, category_slug=self.category2.slug
            )
        )
        expected_qs = [
            repr(quiz)
            for quiz in Quiz.objects.filter(
                author__username=self.user1.username, category__slug=self.category2.slug
            )
        ]
        self.assertQuerysetEqual(
            response.context["quizzes"], expected_qs, ordered=False
        )

    def test_displays_appropriate_message_when_there_are_no_quizzes_that_matches_the_filters(
        self,
    ):
        response = self.client.get(self.get_list_url(author_username="does-not-exists"))
        self.assertContains(response, "There are no quizzes that matches your filters.")

    @patch("quizzes.views.QuizzesListView.paginate_by", 1)
    def test_pagination_when_page_number_is_proper(self):
        response = self.client.get(self.get_list_url(page=1))
        expected_qs = [repr(self.quiz1)]
        self.assertQuerysetEqual(
            response.context["quizzes"], expected_qs, ordered=False
        )

        response = self.client.get(self.get_list_url(page=2))
        expected_qs = [repr(self.quiz2)]
        self.assertQuerysetEqual(
            response.context["quizzes"], expected_qs, ordered=False
        )

        response = self.client.get(self.get_list_url(page=3))
        expected_qs = [repr(self.quiz3)]
        self.assertQuerysetEqual(
            response.context["quizzes"], expected_qs, ordered=False
        )

    def test_pagination_returns_404_when_page_number_is_greater_than_total_number_of_pages(
        self,
    ):
        response = self.client.get(self.get_list_url(page=100))
        self.assertEqual(response.status_code, 404)

    def test_sorting(self):
        self.quiz1.created = datetime.date(2000, 1, 1)
        self.quiz1.save()
        self.create_scores(quiz=self.quiz1, user=self.user1, scores=[100, 75, 80])
        self.quiz2.created = datetime.date(2010, 10, 10)
        self.quiz2.save()
        self.create_scores(quiz=self.quiz2, user=self.user1, scores=[50, 50, 40])
        self.create_question(quiz=self.quiz1, question_body="question")
        self.create_question(quiz=self.quiz1, question_body="question")
        self.create_question(quiz=self.quiz2, question_body="question")

        expected = [repr(quiz) for quiz in [self.quiz1, self.quiz2, self.quiz3]]
        response = self.client.get(self.get_list_url(sorting="created"))
        self.assertQuerysetEqual(response.context["quizzes"], expected)
        response = self.client.get(self.get_list_url(sorting="-created"))
        self.assertQuerysetEqual(response.context["quizzes"], expected[::-1])
        response = self.client.get(self.get_list_url(sorting="avg_score"))
        self.assertQuerysetEqual(response.context["quizzes"], expected[::-1])
        response = self.client.get(self.get_list_url(sorting="-avg_score"))
        self.assertQuerysetEqual(response.context["quizzes"], expected)
        response = self.client.get(self.get_list_url(sorting="length"))
        self.assertQuerysetEqual(response.context["quizzes"], expected[::-1])
        response = self.client.get(self.get_list_url(sorting="-length"))
        self.assertQuerysetEqual(response.context["quizzes"], expected)


class TestQuizDetailView(QuizzesUtilsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.create_category()
        cls.user = cls.create_user()

    def setUp(self):
        self.quiz = self.create_quiz()
        self.question = self.create_question()

    def test_returns_404_when_quiz_with_given_slug_does_not_exists(self):
        response = self.client.get(self.get_quiz_detail_url("does-not-exist"))
        self.assertEqual(response.status_code, 404)

    def test_displays_data_for_given_quiz(self):
        response = self.client.get(self.get_quiz_detail_url(self.QUIZ_SLUG))
        self.assertContains(response, self.category.title)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.QUIZ_DESC)
