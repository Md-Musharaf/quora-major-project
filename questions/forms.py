from django import forms

from .models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "description"]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "What do you want to ask?",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Add more details about your question",
                    "rows": 5,
                }
            ),
        }