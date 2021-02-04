from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from quizzes.models import Quiz, Question, Answer


class QuizCreationForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'category', 'thumbnail']

    def clean(self):
        if Quiz.objects.filter(title=self.cleaned_data['title']):
            raise ValidationError('Quiz with the same title already exists!')

    def save(self, **kwargs):
        commit = kwargs.get('commit', True)
        author = kwargs.get('author', None)
        quiz = super().save(False)
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
            answer = form.cleaned_data.get('answer')
            does_proper_answer_exist = does_proper_answer_exist or form.cleaned_data.get('is_correct')
            if not answer:
                raise ValidationError("Any answer can't be empty!")

        if not does_proper_answer_exist:
            raise ValidationError('At least one of the answers must be marked as correct!')


AnswerFormSet = inlineformset_factory(Question, Answer, formset=BaseAnswerFormSet, fields=['answer', 'is_correct'],
                                      extra=4, can_delete=False)


class BaseQuestionFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.nested = AnswerFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=f'{form.prefix}-{AnswerFormSet.get_default_prefix()}')

    def clean(self):
        if any(self.errors):
            return

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            question = form.cleaned_data.get('question')
            if not question:
                raise ValidationError("Any question can't be empty!")

    def is_valid(self):
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):
        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result


def create_question_formset(number_of_question, can_delete=False):
    return inlineformset_factory(Quiz, Question, formset=BaseQuestionFormSet, fields=['question', 'quiz'],
                                 widgets={'question': forms.Textarea(attrs={'cols': 20, 'rows': 2})},
                                 extra=number_of_question, can_delete=can_delete)
