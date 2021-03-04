from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import AnonymousUser
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin

from quizzes.forms import (
    BaseTakeQuizFormSet,
    FilterSortQuizzesForm,
    QuizForm,
    TakeQuestionForm,
    create_question_formset,
)
from quizzes.models import Quiz, Score

QUIZ_CREATE_SUCCESS_MESSAGE = "Your quiz has been created successfully"
QUIZ_UPDATE_SUCCESS_MESSAGE = "Your quiz has been updated successfully"
QUIZ_DELETE_SUCCESS_MESSAGE = "Your quiz has been deleted successfully"


class QuizWithQuestionsFormView(LoginRequiredMixin, TemplateView):
    template_name = None
    default_number_of_questions = None
    can_delete = False
    object = None
    success_message = None
    success_url = None
    _number_of_questions = None

    def get(self, request, *args, **kwargs):
        QuestionsFormSet = self.get_questions_formset_class()
        context = {
            **self.get_context_data(),
            "quiz_form": QuizForm(instance=self.object),
            "questions_formset": QuestionsFormSet(instance=self.object),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        QuestionsFormSet = self.get_questions_formset_class()
        quiz_form = QuizForm(
            self.request.POST, self.request.FILES, instance=self.object
        )
        questions_formset = QuestionsFormSet(request.POST, instance=self.object)

        if quiz_form.is_valid() and questions_formset.is_valid():
            return self.forms_valid(quiz_form, questions_formset)
        else:
            return self.forms_invalid(quiz_form, questions_formset)

    def get_questions_formset_class(self):
        return create_question_formset(
            self._number_of_questions, can_delete=self.can_delete
        )

    def forms_valid(self, quiz_form, questions_formset):
        quiz = quiz_form.save(author=self.request.user)
        questions_formset.save(quiz=quiz)
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)

    def forms_invalid(self, quiz_form, questions_formset):
        context = {
            **self.get_context_data(),
            "quiz_form": quiz_form,
            "questions_formset": questions_formset,
        }
        return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        self._number_of_questions = self.get_number_of_questions(
            request, default=self.default_number_of_questions
        )

        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get_number_of_questions(request, *, default=10):
        try:
            number_of_questions = int(request.GET["questions"])
        except (ValueError, KeyError):
            return default

        if number_of_questions > 20:
            return 20
        elif number_of_questions < 1:
            return default
        else:
            return number_of_questions

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context["number_of_questions"] = self._number_of_questions
        return context


class CreateQuizWithQuestionsView(QuizWithQuestionsFormView):
    template_name = "quizzes/quiz/create.html"
    default_number_of_questions = 10
    success_message = QUIZ_CREATE_SUCCESS_MESSAGE
    success_url = reverse_lazy("accounts:profile")


class UpdateQuizWithQuestionsView(
    UserPassesTestMixin, SingleObjectMixin, QuizWithQuestionsFormView
):
    template_name = "quizzes/quiz/update.html"
    success_message = QUIZ_UPDATE_SUCCESS_MESSAGE
    success_url = reverse_lazy("accounts:profile")
    can_delete = True
    queryset = Quiz.objects.select_related("author", "category").prefetch_related(
        "questions__answers"
    )

    def dispatch(self, request, *args, **kwargs):
        self.default_number_of_questions = self.get_object().questions.count()
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quiz"] = self.object
        return context

    def test_func(self):
        return self.get_object().author == self.request.user


class DeleteQuizView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    success_url = reverse_lazy("accounts:profile")
    template_name = "quizzes/quiz/confirm_delete.html"
    context_object_name = "quiz"

    def delete(self, *args, **kwargs):
        messages.success(self.request, QUIZ_DELETE_SUCCESS_MESSAGE)
        return super().delete(*args, **kwargs)

    def get_object(self, **kwargs):
        return get_object_or_404(
            self.model.objects.select_related("author"), slug=self.kwargs["slug"]
        )

    def test_func(self):
        return self.get_object().author == self.request.user


def take_quiz(request, slug):
    quiz = get_object_or_404(
        Quiz.objects.select_related("author", "category").prefetch_related(
            "questions__answers"
        ),
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
            score_percentage = calculate_score_percentage(score, number_of_questions)
            if request.user != AnonymousUser():
                Score.objects.create(
                    user=request.user, quiz=quiz, percentage=score_percentage
                )
            return render(
                request,
                "quizzes/quiz/score.html",
                {"quiz": quiz, "score": score, "score_percentage": score_percentage},
            )
    else:
        formset = TakeQuizFormset(quiz=quiz)

    return render(request, "quizzes/quiz/take.html", {"formset": formset, "quiz": quiz})


def calculate_score_percentage(score, number_of_questions):
    return int((score / number_of_questions) * 100)


class QuizzesListView(ListView):
    model = Quiz
    template_name = "quizzes/quiz/list.html"
    paginate_by = 9
    context_object_name = "quizzes"
    author_username = None
    category_slug = None
    sorting = None

    def dispatch(self, request, *args, **kwargs):
        self.author_username = self.request.GET.get("author", "")
        self.category_slug = self.request.GET.get("category", "")
        self.sorting = self.request.GET.get("sorting", "")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.author_username:
            qs = qs.filter(author__username=self.author_username)
        if self.category_slug and self.category_slug != "any":
            qs = qs.filter(category__slug=self.category_slug)
        if self.sorting:
            qs = self.sort_queryset(qs)
        return qs

    def sort_queryset(self, qs):
        asc = True
        sorting = self.sorting
        if self.sorting.startswith("-"):
            sorting = self.sorting[1:]
            asc = False

        if sorting == "created":
            qs = qs.sort_by_date_created(asc)
        elif sorting == "avg_score":
            qs = qs.sort_by_avg_score(asc)
        elif sorting == "length":
            qs = qs.sort_by_number_of_questions(asc)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["author_username"] = self.author_username
        context["category_slug"] = self.category_slug
        context["sorting"] = self.sorting
        context["sort_filter_form"] = FilterSortQuizzesForm(self.request.GET)

        return context


class QuizDetailView(DetailView):
    model = Quiz
    template_name = "quizzes/quiz/detail.html"
    context_object_name = "quiz"

    def get_queryset(self):
        return self.model.objects.select_related("author__profile", "category")
