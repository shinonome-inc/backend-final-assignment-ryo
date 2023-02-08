from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib.auth import get_user_model

from .forms import LoginForm, SignUpForm
from tweets.models import Tweet


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
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweets"] = (
            Tweet.objects.select_related("user")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )
        return context
