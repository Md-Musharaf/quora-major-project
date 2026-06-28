from django import forms

from .models import Answer, Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question

        fields = [
            "title",
            "description",
            "image",
        ]

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
            "image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["content"]

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "placeholder": "Write your answer...",
                    "rows": 6,
                }
            ),
        }

        labels = {
            "content": "",
        }
