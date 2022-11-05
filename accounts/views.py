from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login, authenticate
from .forms import SignUpForm


# Create your views here.
class SignUpView(CreateView):
    template_name = "account/sign_up.html"
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data("username")
        email = form.cleaned_data("email")
        password = form.cleaned_data("password1")
        user = authenticate(username=username, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return response


class HomeView(TemplateView):
    template_name = "accounts/home.html"
