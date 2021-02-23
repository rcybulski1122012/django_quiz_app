from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from quizzes.forms import (BaseTakeQuizFormSet, FilterQuizzesForm, QuizForm,
                           TakeQuestionForm, create_question_formset)
from quizzes.models import Question, Quiz

QUIZ_CREATE_SUCCESS_MESSAGE = "Your quiz has been created successfully"
QUIZ_UPDATE_SUCCESS_MESSAGE = "Your quiz has been updated successfully"
QUIZ_DELETE_SUCCESS_MESSAGE = "Your quiz has been deleted successfully"


@login_required
def create_quiz(request):
    try:
        number_of_questions = int(request.GET["questions"])
    except (ValueError, KeyError):
        number_of_questions = 10

    if number_of_questions > 20:
        number_of_questions = 20
    elif number_of_questions < 1:
        number_of_questions = 10

    QuestionsFormSet = create_question_formset(number_of_questions)

    if request.method == "POST":
        quiz_form = QuizForm(request.POST, request.FILES)
        if quiz_form.is_valid():
            quiz = quiz_form.save(author=request.user, commit=False)
            questions_formset = QuestionsFormSet(request.POST, instance=quiz)
            if questions_formset.is_valid():
                quiz.save()
                questions_formset.save()
                messages.success(
                    request,
                    QUIZ_CREATE_SUCCESS_MESSAGE,
                    extra_tags="alert alert-success",
                )
                return redirect("accounts:profile")
        else:
            questions_formset = QuestionsFormSet(request.POST)
    else:
        quiz_form = QuizForm()
        questions_formset = QuestionsFormSet()

    return render(
        request,
        "quizzes/quiz/create.html",
        {
            "quiz_form": quiz_form,
            "questions_formset": questions_formset,
            "number_of_questions": number_of_questions,
        },
    )


@login_required
def update_quiz(request, slug):
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__answers").select_related("author"),
        slug=slug,
    )
    if quiz.author != request.user:
        raise PermissionDenied()

    number_of_quiz_questions = Question.objects.filter(quiz=quiz).count()

    try:
        number_of_questions = int(request.GET["questions"])
    except (ValueError, KeyError):
        number_of_questions = number_of_quiz_questions
        QuestionsFormSet = create_question_formset(
            number_of_quiz_questions, can_delete=True
        )
    else:
        if number_of_questions < 1:
            number_of_questions = number_of_quiz_questions
        elif number_of_questions > 20:
            number_of_questions = 20
        QuestionsFormSet = create_question_formset(number_of_questions, can_delete=True)

    if request.method == "POST":
        quiz_form = QuizForm(request.POST, request.FILES, instance=quiz)
        questions_formset = QuestionsFormSet(request.POST, instance=quiz)
        if quiz_form.is_valid() and questions_formset.is_valid():
            quiz_form.save()
            questions_formset.save()
            if not Question.objects.filter(quiz=quiz).exists():
                quiz.delete()
            messages.success(
                request, QUIZ_UPDATE_SUCCESS_MESSAGE, extra_tags="alert alert-success"
            )
            return redirect("accounts:profile")
    else:
        quiz_form = QuizForm(instance=quiz)
        questions_formset = QuestionsFormSet(instance=quiz)

    return render(
        request,
        "quizzes/quiz/update.html",
        {
            "questions_formset": questions_formset,
            "quiz_form": quiz_form,
            "quiz": quiz,
            "number_of_questions": number_of_questions,
        },
    )


class DeleteQuizView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    success_url = reverse_lazy("accounts:profile")
    template_name = "quizzes/quiz/confirm_delete.html"
    context_object_name = "quiz"

    def delete(self, request, **kwargs):
        messages.success(
            request, QUIZ_DELETE_SUCCESS_MESSAGE, extra_tags="alert alert-success"
        )
        return super().delete(request, **kwargs)

    def get_object(self, **kwargs):
        return get_object_or_404(
            self.model.objects.select_related("author"), slug=self.kwargs["slug"]
        )

    def test_func(self):
        return self.get_object().author == self.request.user


def take_quiz(request, slug):
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__answers").select_related("author"),
        slug=slug,
    )
    number_of_questions = quiz.questions.count()
    TakeQuizFormset = formset_factory(
        TakeQuestionForm, extra=number_of_questions, formset=BaseTakeQuizFormSet
    )

    if request.method == "POST":
        formset = TakeQuizFormset(data=request.POST, quiz=quiz)
        if formset.is_valid():
            score = formset.get_score()
            score_percentage = int(score / number_of_questions * 100)
            return render(
                request,
                "quizzes/quiz/score.html",
                {"quiz": quiz, "score": score, "score_percentage": score_percentage},
            )
    else:
        formset = TakeQuizFormset(quiz=quiz)

    return render(request, "quizzes/quiz/take.html", {"formset": formset, "quiz": quiz})


class QuizzesListView(ListView):
    model = Quiz
    template_name = "quizzes/quiz/list.html"
    paginate_by = 9
    context_object_name = "quizzes"

    def dispatch(self, *args, **kwargs):
        self.author_username = self.request.GET.get("author", None)
        self.category_slug = self.request.GET.get("category", None)

        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.author_username:
            qs = qs.filter(author__username=self.author_username)
        if self.category_slug:
            qs = qs.filter(category__slug=self.category_slug)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["author_username"] = self.author_username or ""
        context["category_slug"] = self.category_slug or ""
        context["filter_form"] = FilterQuizzesForm()

        return context


class QuizDetailView(DetailView):
    model = Quiz
    template_name = "quizzes/quiz/detail.html"
    context_object_name = "quiz"

    def get_queryset(self):
        return super().get_queryset().select_related("author__profile", "category")
