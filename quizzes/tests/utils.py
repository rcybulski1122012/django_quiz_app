from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

from quizzes.models import Answer, Category, Question, Quiz


class FormSetTestMixin:
    def assertFormsetNumberOfFormsEqual(self, formset, expected):
        number_of_forms = len(formset.forms)
        self.assertEqual(number_of_forms, expected)


class QuizzesUtilsMixin:
    login_url = reverse("accounts:login")
    profile_url = reverse("accounts:profile")
    create_quiz_url = reverse("quizzes:create")

    @staticmethod
    def get_update_quiz_url(slug, questions=""):
        return f'{reverse("quizzes:update", args=[slug])}?questions={questions}'

    @staticmethod
    def get_delete_quiz_url(slug):
        return reverse("quizzes:delete", args=[slug])

    @staticmethod
    def get_take_quiz_url(slug):
        return reverse("quizzes:take", args=[slug])

    @staticmethod
    def get_list_url(page="", author_username="", category_slug=""):
        return f'{reverse("quizzes:list")}?page={page}&author={author_username}&category={category_slug}'

    @staticmethod
    def get_quiz_detail_url(slug):
        return reverse("quizzes:detail", args=[slug])

    USERNAME = "Username123"
    EMAIL = "addressemail123@gmail.com"
    PASSWORD = "SecretPass123"
    CATEGORY_TITLE = "None"

    QUIZ_TITLE = "Quiz title"
    QUIZ_SLUG = slugify(QUIZ_TITLE)
    QUIZ_DESC = "Quiz description"
    QUESTION_BODY = "Question body"

    @staticmethod
    def create_user(username=USERNAME, email=EMAIL, password=PASSWORD):
        return User.objects.create_user(username, email, password)

    @staticmethod
    def create_category(title=CATEGORY_TITLE):
        return Category.objects.create(title=title)

    def create_quiz(
        self, title=QUIZ_TITLE, user=None, category=None, description=QUIZ_DESC
    ):
        user = user or self.user
        category = category or self.category
        return Quiz.objects.create(
            title=title, author=user, category=category, description=description
        )

    def create_question(self, quiz=None, question_body=None):
        quiz = quiz or self.quiz
        question_body = question_body or self.QUESTION_BODY
        question = Question.objects.create(question=question_body, quiz=quiz)
        question.answers.add(Answer(answer="A", is_correct=False), bulk=False)
        question.answers.add(Answer(answer="B", is_correct=False), bulk=False)
        question.answers.add(Answer(answer="C", is_correct=False), bulk=False)
        question.answers.add(Answer(answer="D", is_correct=True), bulk=False)

        return question

    def add_questions_to_quiz(self, n, quiz=None):
        quiz = quiz or self.quiz
        for i in range(n):
            self.create_question(question_body=f"Question{i}", quiz=quiz)

    def post_create_view_with_one_question_quiz(
        self,
        title=QUIZ_TITLE,
        description=QUIZ_DESC,
        category=None,
        thumbnail="",
        question_body=QUESTION_BODY,
        answer_a="A",
        answer_b="B",
        answer_c="C",
        answer_d="D",
        follow=True,
        answer_d_is_correct="on",
    ):
        category = category or self.category.id

        # Always fourth answer is correct!
        data = {
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

        return self.client.post(
            f"{self.create_quiz_url}?questions=1", data=data, follow=follow
        )
