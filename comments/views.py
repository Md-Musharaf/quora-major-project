from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from questions.models import Answer

from .forms import CommentForm
from .models import Comment


def get_safe_redirect(request, fallback_url):
    next_url = request.POST.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return fallback_url


@login_required
@require_POST
def create_comment(request, answer_id):
    answer = get_object_or_404(
        Answer.objects.select_related("question"),
        id=answer_id,
    )

    parent = None
    parent_id = request.POST.get("parent_id")

    if parent_id:
        parent = get_object_or_404(
            Comment,
            id=parent_id,
            answer=answer,
        )

    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.answer = answer
        comment.author = request.user
        comment.parent = parent
        comment.save()

    fallback_url = f"{answer.question.get_absolute_url()}" f"#answer-{answer.id}"

    return redirect(
        get_safe_redirect(
            request,
            fallback_url,
        )
    )


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related(
            "author",
            "answer",
            "answer__question",
        ),
        id=comment_id,
    )

    if comment.author != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = CommentForm(
            request.POST,
            instance=comment,
        )

        if form.is_valid():
            form.save()

            fallback_url = (
                f"{comment.answer.question.get_absolute_url()}" f"#comment-{comment.id}"
            )

            return redirect(
                get_safe_redirect(
                    request,
                    fallback_url,
                )
            )
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "comments/edit_comment.html",
        {
            "form": form,
            "comment": comment,
        },
    )


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related(
            "author",
            "answer",
            "answer__question",
        ),
        id=comment_id,
    )

    if comment.author != request.user:
        raise PermissionDenied

    answer = comment.answer

    if request.method == "POST":
        fallback_url = f"{answer.question.get_absolute_url()}" f"#answer-{answer.id}"

        comment.delete()

        return redirect(
            get_safe_redirect(
                request,
                fallback_url,
            )
        )

    return render(
        request,
        "comments/delete_comment.html",
        {
            "comment": comment,
            "answer": answer,
        },
    )
