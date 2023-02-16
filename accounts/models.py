from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=254)


class FriendShip(models.Model):
    following = models.ForeignKey(
        CustomUser, related_name="following", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        CustomUser, related_name="followed", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["following", "followed"], name="follow_unique"
            ),
        ]
