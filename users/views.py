from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .forms import UserRegistrationForm, ProfileForm
from .models import User

from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from interactions.models import AnswerVote, QuestionVote
from questions.models import Answer, Question

from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import User, UserFollow
from comments.models import Comment


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserRegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    error_message = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("core:home")

        error_message = "Invalid email or password."

    return render(
        request,
        "users/login.html",
        {"error_message": error_message},
    )


def logout_view(request):
    logout(request)
    return redirect("users:login")


@login_required
def profile_view(request):
    return render(
        request,
        "users/profile.html",
        {"profile": request.user.profile},
    )


@login_required
def edit_profile_view(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if form.is_valid():
            form.save()
            return redirect("users:profile")

    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "users/edit_profile.html",
        {"form": form},
    )


def public_profile_view(request, user_id):
    profile_user = get_object_or_404(
        User.objects.select_related("profile"),
        id=user_id,
    )

    questions = (
        Question.objects.filter(
            author=profile_user,
        )
        .annotate(
            answer_count=Count(
                "answers",
                distinct=True,
            ),
            vote_count=Count(
                "votes",
                distinct=True,
            ),
        )
        .prefetch_related("topics")
        .order_by("-created_at")
    )

    answers = (
        Answer.objects.filter(
            author=profile_user,
        )
        .select_related("question")
        .annotate(
            vote_count=Count(
                "votes",
                distinct=True,
            ),
        )
        .order_by("-created_at")
    )

    activity_questions = list(
        Question.objects.filter(
            author=profile_user,
        ).order_by(
            "-created_at"
        )[:10]
    )

    activity_answers = list(
        Answer.objects.filter(
            author=profile_user,
        )
        .select_related("question")
        .order_by("-created_at")[:10]
    )

    activity_comments = list(
        Comment.objects.filter(
            author=profile_user,
        )
        .select_related(
            "answer",
            "answer__question",
        )
        .order_by("-created_at")[:10]
    )

    for question in activity_questions:
        question.activity_type = "question"

    for answer in activity_answers:
        answer.activity_type = "answer"

    for comment in activity_comments:
        comment.activity_type = "comment"

    activity_items = sorted(
        activity_questions + activity_answers + activity_comments,
        key=lambda item: item.created_at,
        reverse=True,
    )[:20]

    question_upvotes = QuestionVote.objects.filter(
        question__author=profile_user,
    ).count()

    answer_upvotes = AnswerVote.objects.filter(
        answer__author=profile_user,
    ).count()

    total_upvotes_received = question_upvotes + answer_upvotes

    active_tab = request.GET.get(
        "tab",
        "profile",
    )

    allowed_tabs = {
        "profile",
        "questions",
        "answers",
        "activity",
        "followers",
        "following",
    }

    if active_tab not in allowed_tabs:
        active_tab = "profile"

    followers_count = profile_user.follower_relationships.count()

    following_count = profile_user.following_relationships.count()

    is_following = False

    if request.user.is_authenticated:
        is_following = UserFollow.objects.filter(
            follower=request.user,
            following=profile_user,
        ).exists()

    followers = (
        UserFollow.objects.filter(
            following=profile_user,
        )
        .select_related(
            "follower",
            "follower__profile",
        )
        .order_by("-created_at")
    )

    following = (
        UserFollow.objects.filter(
            follower=profile_user,
        )
        .select_related(
            "following",
            "following__profile",
        )
        .order_by("-created_at")
    )

    followers_count = followers.count()
    following_count = following.count()

    context = {
        "profile_user": profile_user,
        "profile": profile_user.profile,
        "questions": questions,
        "answers": answers,
        "followers": followers,
        "following": following,
        "activity_items": activity_items,
        "question_count": questions.count(),
        "answer_count": answers.count(),
        "total_upvotes_received": total_upvotes_received,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": active_tab,
    }

    return render(
        request,
        "users/public_profile.html",
        context,
    )


@login_required
@require_POST
def toggle_follow_view(request, user_id):
    profile_user = get_object_or_404(
        User,
        id=user_id,
    )

    # A user cannot follow themselves
    if request.user == profile_user:
        return redirect(
            "users:public_profile",
            user_id=profile_user.id,
        )

    follow_relationship, created = UserFollow.objects.get_or_create(
        follower=request.user,
        following=profile_user,
    )

    # If the relationship already existed, unfollow the user
    if not created:
        follow_relationship.delete()

    next_url = request.POST.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect(
        "users:public_profile",
        user_id=profile_user.id,
    )
