from django import forms

from .models import Answer, Question
from topics.models import Topic


class QuestionForm(forms.ModelForm):
    existing_topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Select existing topics",
    )

    new_topics = forms.CharField(
        required=False,
        label="Add new topics",
        help_text="Enter topics separated by commas. Maximum 5 topics in total.",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Example: Django, Python, Web Development",
            }
        ),
    )

    class Meta:
        model = Question
        fields = [
            "title",
            "description",
            "image",
            "existing_topics",
            "new_topics",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["existing_topics"].initial = self.instance.topics.all()

    def clean(self):
        cleaned_data = super().clean()

        existing_topics = cleaned_data.get("existing_topics")
        raw_new_topics = cleaned_data.get("new_topics", "")

        # Remove extra spaces, empty values, and duplicate new topics.
        new_topic_names = []
        seen_names = set()

        for topic_name in raw_new_topics.split(","):
            topic_name = " ".join(topic_name.strip().split())

            if not topic_name:
                continue

            normalized_name = topic_name.casefold()

            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                new_topic_names.append(topic_name)

        # Do not count a newly entered topic if the same existing topic
        # has already been selected.
        existing_topic_names = set()

        if existing_topics is not None:
            existing_topic_names = {topic.name.casefold() for topic in existing_topics}

        new_topic_names = [
            topic_name
            for topic_name in new_topic_names
            if topic_name.casefold() not in existing_topic_names
        ]

        existing_topic_count = (
            existing_topics.count() if existing_topics is not None else 0
        )

        total_topic_count = existing_topic_count + len(new_topic_names)

        if total_topic_count > 5:
            raise forms.ValidationError("A question can have a maximum of 5 topics.")

        # Save the cleaned list for use inside the view.
        cleaned_data["new_topic_names"] = new_topic_names

        return cleaned_data


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
