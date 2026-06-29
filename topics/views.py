from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Topic, TopicFollow


def topic_detail(request, slug):
    topic = get_object_or_404(
        Topic.objects.prefetch_related(
            "questions",
            "questions__author",
            "questions__author__profile",
        ),
        slug=slug,
    )

    questions = topic.questions.all().order_by("-created_at")

    is_following = False

    if request.user.is_authenticated:
        is_following = TopicFollow.objects.filter(
            user=request.user,
            topic=topic,
        ).exists()

    followers_count = topic.followers.count()
    
    context = {
        "topic": topic,
        "questions": questions,
        "is_following": is_following,
        "followers_count": followers_count,
    }

    return render(
        request,
        "topics/topic_detail.html",
        context,
    )


@login_required
@require_POST
def toggle_topic_follow(request, slug):
    topic = get_object_or_404(
        Topic,
        slug=slug,
    )

    topic_follow, created = TopicFollow.objects.get_or_create(
        user=request.user,
        topic=topic,
    )

    if not created:
        topic_follow.delete()

    return redirect(
        "topics:detail",
        slug=topic.slug,
    )
