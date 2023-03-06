from django.urls import path, include
from django.conf import settings

from . import views

app_name = "tweets"
urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("create/", views.TweetCreateView.as_view(), name="create"),
    path("<int:pk>/", views.TweetDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.TweetDeleteView.as_view(), name="delete"),
    # path("<int:pk>/like/", views.LikeView, name="like"),
    # path("<int:pk>/unlike/", views.UnlikeView, name="unlike"),
]

if settings.SQL_DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
