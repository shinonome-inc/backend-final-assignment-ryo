from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


CustomUser = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.CharField()

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )
