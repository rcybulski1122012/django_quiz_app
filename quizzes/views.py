from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from quizzes.forms import QuizForm, create_question_formset
from quizzes.models import Quiz, Question


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
                messages.success(request, 'Your quiz has been created successfully', extra_tags='alert alert-success')
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
def update_quiz(request, quiz_slug):
    quiz = get_object_or_404(Quiz.objects.select_related('author').prefetch_related('questions__answers'),
                             slug=quiz_slug)
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
            messages.success(request, 'Your quiz has been updated successfully', extra_tags='alert alert-success')
            return redirect('accounts:profile')
    else:
        quiz_form = QuizForm(instance=quiz)
        questions_formset = QuestionsFormSet(instance=quiz)

    return render(request, 'quizzes/quiz/update.html', {'questions_formset': questions_formset,
                                                        'quiz_form': quiz_form, 'quiz': quiz})
