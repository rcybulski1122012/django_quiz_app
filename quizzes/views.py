from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from quizzes.forms import QuizCreationForm, create_question_formset


@login_required
def create_quiz(request):
    number_of_questions = get_number_of_questions(request)
    QuestionFormSet = create_question_formset(number_of_questions)

    if request.method == 'POST':
        quiz_form = QuizCreationForm(request.POST, request.FILES)
        if quiz_form.is_valid():
            quiz = quiz_form.save(author=request.user, commit=False)
            question_formset = QuestionFormSet(request.POST, instance=quiz)
            if question_formset.is_valid():
                quiz.save()
                question_formset.save()
                messages.success(request, 'Your quiz has been created successfully', extra_tags='alert alert-success')
                return redirect('accounts:profile')
        else:
            question_formset = QuestionFormSet(request.POST)
    else:
        quiz_form = QuizCreationForm()
        question_formset = QuestionFormSet()

    return render(request, 'quizzes/create_quiz.html', {
        'quiz_form': quiz_form,
        'question_formset': question_formset,
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
