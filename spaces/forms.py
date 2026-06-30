from django import forms

from .models import Space, SpacePost


class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space

        fields = (
            "name",
            "description",
            "icon",
            "cover_image",
            "topics",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-gray-300 "
                        "px-4 py-3 focus:border-red-500 "
                        "focus:outline-none focus:ring-1 focus:ring-red-500"
                    ),
                    "placeholder": "Enter Space name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-gray-300 "
                        "px-4 py-3 focus:border-red-500 "
                        "focus:outline-none focus:ring-1 focus:ring-red-500"
                    ),
                    "rows": 5,
                    "placeholder": "What is this Space about?",
                }
            ),
            "icon": forms.ClearableFileInput(
                attrs={
                    "class": "w-full rounded-lg border border-gray-300 px-4 py-3",
                }
            ),
            "cover_image": forms.ClearableFileInput(
                attrs={
                    "class": "w-full rounded-lg border border-gray-300 px-4 py-3",
                }
            ),
            "topics": forms.SelectMultiple(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-gray-300 "
                        "px-4 py-3 focus:border-red-500 focus:outline-none"
                    ),
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        queryset = Space.objects.filter(
            name__iexact=name,
        )

        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise forms.ValidationError("A Space with this name already exists.")

        return name


class SpacePostForm(forms.ModelForm):
    class Meta:
        model = SpacePost

        fields = (
            "title",
            "content",
            "image",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-gray-300 "
                        "bg-white px-4 py-3 text-gray-900 "
                        "placeholder-gray-400 focus:border-red-500 "
                        "focus:outline-none focus:ring-1 focus:ring-red-500 "
                        "dark:border-gray-600 dark:bg-gray-800 "
                        "dark:text-gray-100 dark:placeholder-gray-500"
                    ),
                    "placeholder": "Post title (optional)",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-gray-300 "
                        "bg-white px-4 py-3 text-gray-900 "
                        "placeholder-gray-400 focus:border-red-500 "
                        "focus:outline-none focus:ring-1 focus:ring-red-500 "
                        "dark:border-gray-600 dark:bg-gray-800 "
                        "dark:text-gray-100 dark:placeholder-gray-500"
                    ),
                    "rows": 7,
                    "placeholder": "Write something for this Space...",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-gray-300 "
                        "bg-white px-3 py-3 text-sm text-gray-700 "
                        "dark:border-gray-600 dark:bg-gray-800 "
                        "dark:text-gray-200"
                    ),
                }
            ),
        }

    def clean_title(self):
        return self.cleaned_data.get("title", "").strip()

    def clean_content(self):
        content = self.cleaned_data["content"].strip()

        if not content:
            raise forms.ValidationError("Post content cannot be empty.")

        return content
