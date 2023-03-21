from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=254)


class FriendShip(models.Model):
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="followings")
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["following", "follower"], name="follow_unique"),
        ]
