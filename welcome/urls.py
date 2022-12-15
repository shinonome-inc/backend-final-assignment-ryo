from django.urls import path

from . import views

app_name = "welcome"
urlpatterns = [
    path("index/", views.WelcomeView.as_view(), name="index"),
]
