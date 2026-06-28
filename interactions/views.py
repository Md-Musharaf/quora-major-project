from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from questions.models import Answer, Question

from .models import AnswerVote, QuestionVote


@login_required
@require_POST
def toggle_question_vote(request, question_id):
    question = get_object_or_404(
        Question,
        id=question_id,
    )

    vote = QuestionVote.objects.filter(
        user=request.user,
        question=question,
    ).first()

    if vote:
        vote.delete()
    else:
        QuestionVote.objects.create(
            user=request.user,
            question=question,
        )

    next_url = request.POST.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect(
        "questions:detail",
        question_id=question.id,
    )


@login_required
@require_POST
def toggle_answer_vote(request, answer_id):
    answer = get_object_or_404(
        Answer.objects.select_related("question"),
        id=answer_id,
    )

    vote = AnswerVote.objects.filter(
        user=request.user,
        answer=answer,
    ).first()

    if vote:
        vote.delete()
    else:
        AnswerVote.objects.create(
            user=request.user,
            answer=answer,
        )

    next_url = request.POST.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect(
        "questions:detail",
        question_id=answer.question_id,
    )
