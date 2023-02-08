from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DeleteView, DetailView, ListView


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"


# Create your views here.
