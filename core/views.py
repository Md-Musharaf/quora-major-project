from django.shortcuts import render

from questions.models import Question


def home(request):
    questions = Question.objects.select_related(
        "author",
        "author__profile",
    ).all()

    context = {
        "questions": questions,
    }

    return render(request, "core/home.html", context)