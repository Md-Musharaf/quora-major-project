from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import SpaceForm, SpacePostForm
from .models import Space, SpaceFollow, SpacePost
from django.db.models import Count, Exists, OuterRef


def space_list(request):
    spaces = Space.objects.select_related(
        "owner",
        "owner__profile",
    ).prefetch_related("topics")

    return render(
        request,
        "spaces/space_list.html",
        {
            "spaces": spaces,
        },
    )


def space_detail(request, slug):
    follows = SpaceFollow.objects.filter(
        space=OuterRef("pk"),
    )

    if request.user.is_authenticated:
        follows = follows.filter(
            user=request.user,
        )

    space_queryset = (
        Space.objects.select_related(
            "owner",
            "owner__profile",
        )
        .prefetch_related("topics")
        .annotate(
            follower_count=Count(
                "follows",
                distinct=True,
            ),
        )
    )

    if request.user.is_authenticated:
        space_queryset = space_queryset.annotate(
            is_following=Exists(follows),
        )

    space = get_object_or_404(
        space_queryset,
        slug=slug,
    )

    if not request.user.is_authenticated:
        space.is_following = False

    posts = SpacePost.objects.filter(space=space).select_related(
        "author",
        "author__profile",
    )

    return render(
        request,
        "spaces/space_detail.html",
        {
            "space": space,
            "posts": posts,
        },
    )


@login_required
@require_POST
def toggle_space_follow(request, slug):
    space = get_object_or_404(
        Space,
        slug=slug,
    )

    if space.owner_id == request.user.id:
        return redirect(
            "spaces:detail",
            slug=space.slug,
        )

    follow = SpaceFollow.objects.filter(
        space=space,
        user=request.user,
    ).first()

    if follow:
        follow.delete()
    else:
        SpaceFollow.objects.create(
            space=space,
            user=request.user,
        )

    return redirect(
        "spaces:detail",
        slug=space.slug,
    )


@login_required
def create_space(request):
    if request.method == "POST":
        form = SpaceForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            space = form.save(commit=False)
            space.owner = request.user
            space.save()
            form.save_m2m()

            return redirect(
                "spaces:detail",
                slug=space.slug,
            )
    else:
        form = SpaceForm()

    return render(
        request,
        "spaces/space_form.html",
        {
            "form": form,
            "page_title": "Create Space",
            "submit_text": "Create Space",
        },
    )


@login_required
def edit_space(request, slug):
    space = get_object_or_404(
        Space,
        slug=slug,
    )

    if space.owner_id != request.user.id:
        raise PermissionDenied("You are not allowed to edit this Space.")

    if request.method == "POST":
        form = SpaceForm(
            request.POST,
            request.FILES,
            instance=space,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "spaces:detail",
                slug=space.slug,
            )
    else:
        form = SpaceForm(
            instance=space,
        )

    return render(
        request,
        "spaces/space_form.html",
        {
            "form": form,
            "space": space,
            "page_title": "Edit Space",
            "submit_text": "Save Changes",
        },
    )


@login_required
@require_POST
def delete_space(request, slug):
    space = get_object_or_404(
        Space,
        slug=slug,
    )

    if space.owner_id != request.user.id:
        raise PermissionDenied("You are not allowed to delete this Space.")

    space.delete()

    return redirect("spaces:list")


@login_required
def create_space_post(request, slug):
    space = get_object_or_404(
        Space,
        slug=slug,
    )

    if space.owner_id != request.user.id:
        raise PermissionDenied("Only the Space owner can create posts.")

    if request.method == "POST":
        form = SpacePostForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            post = form.save(commit=False)
            post.space = space
            post.author = request.user
            post.save()

            return redirect(
                "spaces:detail",
                slug=space.slug,
            )
    else:
        form = SpacePostForm()

    return render(
        request,
        "spaces/space_post_form.html",
        {
            "form": form,
            "space": space,
            "page_title": "Create Post",
            "submit_text": "Publish Post",
        },
    )


@login_required
def edit_space_post(request, slug, post_id):
    space = get_object_or_404(
        Space,
        slug=slug,
    )

    post = get_object_or_404(
        SpacePost,
        id=post_id,
        space=space,
    )

    if post.author_id != request.user.id:
        raise PermissionDenied("You are not allowed to edit this post.")

    if request.method == "POST":
        form = SpacePostForm(
            request.POST,
            request.FILES,
            instance=post,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "spaces:detail",
                slug=space.slug,
            )
    else:
        form = SpacePostForm(
            instance=post,
        )

    return render(
        request,
        "spaces/space_post_form.html",
        {
            "form": form,
            "space": space,
            "post": post,
            "page_title": "Edit Post",
            "submit_text": "Save Changes",
        },
    )


@login_required
def delete_space_post(request, slug, post_id):
    space = get_object_or_404(
        Space,
        slug=slug,
    )

    post = get_object_or_404(
        SpacePost,
        id=post_id,
        space=space,
    )

    if post.author_id != request.user.id:
        raise PermissionDenied("You are not allowed to delete this post.")

    if request.method == "POST":
        post.delete()

        return redirect(
            "spaces:detail",
            slug=space.slug,
        )

    return render(
        request,
        "spaces/space_post_confirm_delete.html",
        {
            "space": space,
            "post": post,
        },
    )
