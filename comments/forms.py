from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Write a comment...",
                    "class": (
                        "w-full resize-none rounded-lg border border-gray-300 "
                        "px-3 py-2 text-sm focus:border-blue-500 "
                        "focus:outline-none focus:ring-1 focus:ring-blue-500"
                    ),
                }
            )
        }
