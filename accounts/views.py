from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model, login, authenticate
from .forms import SignUpForm

CustomUser = get_user_model()

# Create your views here.
class SignUpView(CreateView):
    model = CustomUser
    template_name = "account/sign_up.html"
    form_class = SignUpForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data("username")
        email = form.cleaned_data("email")
        password = form.cleaned_data("password1")
        user = authenticate(username=username, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return response
