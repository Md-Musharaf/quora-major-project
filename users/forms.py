from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Profile, User


class UserRegistrationForm(UserCreationForm):
    display_name = forms.CharField(
        max_length=100,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "email",
            "display_name",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            profile, created = Profile.objects.get_or_create(user=user)

            profile.display_name = self.cleaned_data["display_name"]
            profile.save()

        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "display_name",
            "bio",
            "profile_picture",
            "location",
            "profession",
            "website",
        ]
