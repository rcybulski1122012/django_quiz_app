from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.forms import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from quizzes.forms import QuizForm, create_question_formset, TakeQuestionForm, BaseTakeQuizFormSet
from quizzes.models import Quiz, Question


QUIZ_CREATE_SUCCESS_MESSAGE = 'Your quiz has been created successfully'
QUIZ_UPDATE_SUCCESS_MESSAGE = 'Your quiz has been updated successfully'
QUIZ_DELETE_SUCCESS_MESSAGE = 'Your quiz has been deleted successfully'


@login_required
def create_quiz(request):
    number_of_questions = get_number_of_questions(request)
    QuestionsFormSet = create_question_formset(number_of_questions)

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, request.FILES)
        if quiz_form.is_valid():
            quiz = quiz_form.save(author=request.user, commit=False)
            questions_formset = QuestionsFormSet(request.POST, instance=quiz)
            if questions_formset.is_valid():
                quiz.save()
                questions_formset.save()
                messages.success(request, QUIZ_CREATE_SUCCESS_MESSAGE, extra_tags='alert alert-success')
                return redirect('accounts:profile')
        else:
            questions_formset = QuestionsFormSet(request.POST)
    else:
        quiz_form = QuizForm()
        questions_formset = QuestionsFormSet()

    return render(request, 'quizzes/quiz/create.html', {
        'quiz_form': quiz_form,
        'questions_formset': questions_formset,
    })


def get_number_of_questions(request):
    try:
        number_of_questions = int(request.GET.get('questions', 10))
    except ValueError:
        number_of_questions = 10
    else:
        # 20 is max number of questions
        if number_of_questions > 20:
            number_of_questions = 20
        elif number_of_questions < 1:
            number_of_questions = 10
    return number_of_questions


@login_required
def update_quiz(request, slug):
    quiz = get_object_or_404(Quiz.objects.select_related('author').prefetch_related('questions__answers'),
                             slug=slug)
    if quiz.author != request.user:
        raise PermissionDenied()

    number_of_questions = get_number_of_questions(request)
    number_of_quiz_questions = Question.objects.filter(quiz=quiz).count()

    if number_of_questions < number_of_quiz_questions and request.GET.get('questions'):
        number_of_questions = number_of_quiz_questions
    QuestionsFormSet = create_question_formset(number_of_questions, can_delete=True)

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, request.FILES, instance=quiz)
        questions_formset = QuestionsFormSet(request.POST, instance=quiz)
        if quiz_form.is_valid() and questions_formset.is_valid():
            quiz_form.save()
            questions_formset.save()
            if not Question.objects.filter(quiz=quiz).exists():
                quiz.delete()
            messages.success(request, QUIZ_UPDATE_SUCCESS_MESSAGE, extra_tags='alert alert-success')
            return redirect('accounts:profile')
    else:
        quiz_form = QuizForm(instance=quiz)
        questions_formset = QuestionsFormSet(instance=quiz)

    return render(request, 'quizzes/quiz/update.html', {'questions_formset': questions_formset,
                                                        'quiz_form': quiz_form, 'quiz': quiz})


class DeleteQuizView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    success_url = reverse_lazy('accounts:profile')
    template_name = 'quizzes/quiz/confirm_delete.html'
    context_object_name = 'quiz'

    def delete(self, request, **kwargs):
        messages.success(request, QUIZ_DELETE_SUCCESS_MESSAGE, extra_tags='alert alert-success')
        return super().delete(request, **kwargs)

    def get_object(self, **kwargs):
        return self.model.objects.select_related('author').get(slug=self.kwargs['slug'])

    def test_func(self):
        return self.get_object().author == self.request.user


def take_quiz(request, slug):
    quiz = get_object_or_404(Quiz.objects.select_related('author').prefetch_related('questions__answers'), slug=slug)
    number_of_questions = quiz.questions.count()
    TakeQuizFormset = formset_factory(TakeQuestionForm, extra=number_of_questions, formset=BaseTakeQuizFormSet)

    if request.method == 'POST':
        formset = TakeQuizFormset(data=request.POST, quiz=quiz)
        if formset.is_valid():
            score = formset.get_score()
            score_percentage = int(score / number_of_questions * 100)
            return render(request, 'quizzes/quiz/score.html', {'quiz': quiz, 'score': score,
                                                               'score_percentage': score_percentage})
    else:
        formset = TakeQuizFormset(quiz=quiz)

    return render(request, 'quizzes/quiz/take.html', {'formset': formset, 'quiz': quiz})

