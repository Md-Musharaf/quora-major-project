from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Value,
)
from django.shortcuts import get_object_or_404, redirect, render

from interactions.models import AnswerVote

from .forms import AnswerForm, QuestionForm
from .models import Answer, Question

from comments.models import Comment


@login_required
def create_question(request):
    if request.method == "POST":
        form = QuestionForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            return redirect("home")
    else:
        form = QuestionForm()

    return render(
        request,
        "questions/create_question.html",
        {"form": form},
    )


def question_detail(request, question_id):
    comments = Comment.objects.select_related(
        "author",
        "author__profile",
    ).order_by("created_at")

    answers = (
        Answer.objects.select_related(
            "author",
            "author__profile",
        )
        .prefetch_related(
            Prefetch(
                "comments",
                queryset=comments,
                to_attr="all_comments",
            )
        )
        .annotate(
            vote_count=Count("votes", distinct=True),
        )
    )

    if request.user.is_authenticated:
        answers = answers.annotate(
            user_has_voted=Exists(
                AnswerVote.objects.filter(
                    answer_id=OuterRef("pk"),
                    user=request.user,
                )
            )
        )
    else:
        answers = answers.annotate(
            user_has_voted=Value(
                False,
                output_field=BooleanField(),
            )
        )

    question = get_object_or_404(
        Question.objects.select_related(
            "author",
            "author__profile",
        ).prefetch_related(
            Prefetch(
                "answers",
                queryset=answers,
            )
        ),
        id=question_id,
    )

    # Build the nested comment tree for every answer.
    for answer in question.answers.all():
        comments_by_id = {comment.id: comment for comment in answer.all_comments}

        for comment in answer.all_comments:
            comment.thread_replies = []

        root_comments = []

        for comment in answer.all_comments:
            if comment.parent_id and comment.parent_id in comments_by_id:
                parent = comments_by_id[comment.parent_id]
                parent.thread_replies.append(comment)
            else:
                root_comments.append(comment)

        answer.root_comments = root_comments

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("users:login")

        answer_form = AnswerForm(request.POST)

        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()

            return redirect(
                "questions:detail",
                question_id=question.id,
            )
    else:
        answer_form = AnswerForm()

    user_has_voted = False

    if request.user.is_authenticated:
        user_has_voted = question.votes.filter(
            user=request.user,
        ).exists()

    context = {
        "question": question,
        "answer_form": answer_form,
        "user_has_voted": user_has_voted,
    }

    return render(
        request,
        "questions/question_detail.html",
        context,
    )


@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if question.author != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = QuestionForm(
            request.POST,
            request.FILES,
            instance=question,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "questions:detail",
                question_id=question.id,
            )
    else:
        form = QuestionForm(instance=question)

    return render(
        request,
        "questions/edit_question.html",
        {
            "form": form,
            "question": question,
        },
    )


@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if question.author != request.user:
        raise PermissionDenied

    if request.method == "POST":
        question.delete()
        return redirect("home")

    return render(
        request,
        "questions/delete_question.html",
        {"question": question},
    )


@login_required
def edit_answer(request, answer_id):
    answer = get_object_or_404(
        Answer.objects.select_related("question", "author"),
        id=answer_id,
    )

    if answer.author != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = AnswerForm(
            request.POST,
            instance=answer,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "questions:detail",
                question_id=answer.question.id,
            )
    else:
        form = AnswerForm(instance=answer)

    return render(
        request,
        "questions/edit_answer.html",
        {
            "form": form,
            "answer": answer,
        },
    )


@login_required
def delete_answer(request, answer_id):
    answer = get_object_or_404(
        Answer.objects.select_related("question", "author"),
        id=answer_id,
    )

    if answer.author != request.user:
        raise PermissionDenied

    question_id = answer.question.id

    if request.method == "POST":
        answer.delete()

        return redirect(
            "questions:detail",
            question_id=question_id,
        )

    return render(
        request,
        "questions/delete_answer.html",
        {"answer": answer},
    )
