from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, BaseInlineFormSet, inlineformset_factory

from quizzes.models import Answer, Category, Question, Quiz

SAME_QUIZ_TITLE_ERROR = "Quiz with the same title already exists!"
ALL_ANSWERS_INCORRECT_ERROR = "At least one of the answers must be marked as correct!"


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "description", "category", "thumbnail"]

    def clean(self):
        title = self.cleaned_data["title"]
        if Quiz.objects.filter(title=title).exists() and self.instance.title != title:
            raise ValidationError(SAME_QUIZ_TITLE_ERROR)

    def save(self, **kwargs):
        commit = kwargs.get("commit", True)
        author = kwargs.get("author", None)
        quiz = super().save(False)
        if author:
            quiz.author = author
        if commit:
            quiz.save()
        return quiz


class BaseAnswerFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        does_proper_answer_exist = False
        for form in self.forms:
            does_proper_answer_exist = (
                does_proper_answer_exist or form.cleaned_data.get("is_correct")
            )

        if not does_proper_answer_exist:
            raise ValidationError(ALL_ANSWERS_INCORRECT_ERROR)


AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    formset=BaseAnswerFormSet,
    fields=["answer", "is_correct"],
    extra=4,
    max_num=4,
    min_num=4,
    can_delete=False,
)


class BaseQuestionFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.nested = AnswerFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=f"{form.prefix}-{AnswerFormSet.get_default_prefix()}",
        )

    def is_valid(self):
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, "nested"):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):
        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, "nested"):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result


def create_question_formset(number_of_questions, can_delete=False):
    return inlineformset_factory(
        Quiz,
        Question,
        formset=BaseQuestionFormSet,
        fields=["question", "quiz"],
        widgets={"question": forms.Textarea(attrs={"cols": 20, "rows": 2})},
        extra=number_of_questions,
        min_num=number_of_questions,
        max_num=number_of_questions,
        can_delete=can_delete,
    )


class TakeQuestionForm(forms.Form):
    answer = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect)

    def set_question(self, question):
        self.fields["answer"].queryset = question.answers
        self.fields["answer"].label = question.question


class BaseTakeQuizFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop("quiz")
        super().__init__(*args, **kwargs)
        for form, question in zip(self.forms, quiz.questions.all()):
            form.set_question(question)

    def get_score(self):
        score = 0
        for form in self.forms:
            cd = form.cleaned_data
            try:
                if cd["answer"].is_correct:
                    score += 1
            except KeyError:
                pass
        return score


class FilterQuizzesForm(forms.Form):
    author = forms.CharField(required=False)
    category = forms.ChoiceField(
        choices=[
            (category.slug, category.slug.capitalize())
            for category in Category.objects.all()
        ]
    )
