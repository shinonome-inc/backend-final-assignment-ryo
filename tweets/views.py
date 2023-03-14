from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import TweetCreateForm
from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    model = Tweet
    context_object_name = "tweet_list"
    queryset = Tweet.objects.select_related("user").annotate(like_num=Count("like")).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweet_list = []
        for tweet in context["tweet_list"]:
            liked = False
            if tweet.like_set.filter(user=self.request.user).exists():
                liked = True
            tweet.liked = liked
            tweet_list.append(tweet)
        context["tweet_list"] = tweet_list
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    template_name = "tweets/tweet_create.html"
    form_class = TweetCreateForm
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    template_name = "tweets/tweet_detail.html"
    model = Tweet
    context_object_name = "tweet_detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweet = self.get_object()
        liked = False
        if tweet.like_set.filter(user=self.request.user).exists():
            liked = True
        context["like_num"] = self.object.like_set.count()
        context["liked"] = liked
        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "tweets/tweet_delete.html"
    model = Tweet
    success_url = reverse_lazy("tweets:home")
    context_object_name = "tweet_delete"

    def test_func(self):
        tweet = self.get_object()
        return self.request.user == tweet.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        Like.objects.get_or_create(tweet=tweet, user=request.user)
        like_count = tweet.like_set.count()
        context = {
            "like_num": like_count,
            "tweet_pk": tweet.pk,
            "liked": True,
        }
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        Like.objects.filter(tweet=tweet, user=user).delete()
        like_count = tweet.like_set.count()
        context = {
            "like_num": like_count,
            "tweet_pk": tweet.pk,
            "liked": False,
        }
        return JsonResponse(context)
