from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, TemplateView
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect, render, get_object_or_404

from .forms import LoginForm, SignUpForm
from tweets.models import Tweet
from .models import FriendShip


User = get_user_model()


# Create your views here.
class UserSignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        user = authenticate(username=username, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return response
        else:
            return HttpResponse("もう一度やり直してください")


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"


class UserLogoutView(LogoutView):
    pass


class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = "accounts/profile.html"
    model = User
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["tweet_list"] = (
            Tweet.objects.select_related("user")
            .filter(user=self.object)
            .order_by("-created_at")
        )
        context["is_following"] = FriendShip.objects.filter(
            following=user, followed=self.request.user
        ).exists()
        context["followings_num"] = FriendShip.objects.filter(
            followed=self.object
        ).count()
        context["followers_num"] = FriendShip.objects.filter(
            following=self.object
        ).count()
        return context


class FollowView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/follow.html"

    def post(self, request, *args, **kwargs):
        following = get_object_or_404(User, username=self.kwargs["username"])
        follower = self.request.user
        if following == follower:
            messages.warning(request, "自分自身はフォローできません。")
            return render(request, "accounts/follow.html")
        elif FriendShip.objects.filter(following=following, followed=follower).exists():
            messages.warning(request, "すでにフォローしています。")
            return render(request, "accounts/follow.html")
        else:
            FriendShip.objects.create(following=following, followed=follower)
        return HttpResponseRedirect(reverse_lazy("tweets:home"))


class UnFollowView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/unfollow.html"

    def post(self, request, *args, **kwargs):
        following = get_object_or_404(User, username=self.kwargs["username"])
        unfollow = FriendShip.objects.filter(following=following, followed=request.user)

        if unfollow.exists():
            unfollow.delete()
            return HttpResponseRedirect(reverse_lazy("tweets:home"))
        else:
            messages.warning(request, "無効な操作です。")
            return render(request, "accounts/unfollow.html")


class FollowingListView(LoginRequiredMixin, ListView):
    template_name = "accounts/following_list.html"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["following_list"] = FriendShip.objects.select_related(
            "following"
        ).filter(followed=user)
        return context


class FollowerListView(LoginRequiredMixin, ListView):
    template_name = "accounts/follower_list.html"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["follower_list"] = FriendShip.objects.select_related("followed").filter(
            following=user
        )
        return context
