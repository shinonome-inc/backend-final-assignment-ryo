from django.forms import ModelForm

from .models import Tweet


class TweetCreateForm(ModelForm):
    class Meta:
        model = Tweet
        fields = ("content",)
