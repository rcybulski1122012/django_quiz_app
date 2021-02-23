from django.test import SimpleTestCase

from quizzes.templatetags.quizzes_utils import \
    get_number_of_questions_placeholder


class TestQuestionPlaceHolderTemplateTag(SimpleTestCase):
    def test_returns_given_number_when_it_is_proper(self):
        result = get_number_of_questions_placeholder("12")
        self.assertEqual(result, 12)

    def test_returns_10_when_number_is_not_given(self):
        result = get_number_of_questions_placeholder("")
        self.assertEqual(result, 10)

    def test_returns_10_when_given_number_is_less_than_1(self):
        result = get_number_of_questions_placeholder("0")
        self.assertEqual(result, 10)

        result = get_number_of_questions_placeholder("-5")
        self.assertEqual(result, 10)

    def test_returns_20_when_given_number_is_greater_than_20(self):
        result = get_number_of_questions_placeholder("123")
        self.assertEqual(result, 20)

    def test_returns_10_when_given_value_is_not_number(self):
        result = get_number_of_questions_placeholder("hi")
        self.assertEqual(result, 10)
