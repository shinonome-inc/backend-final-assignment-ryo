from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        self.post1 = Tweet.objects.create(user=self.user, content="testpost1")
        self.post2 = Tweet.objects.create(user=self.user, content="testpost2")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")
        self.assertQuerysetEqual(
            response.context["tweet_list"],
            Tweet.objects.order_by("-created_at"),
            ordered=False,
        )


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/tweet_create.html")

    def test_success_post(self):
        response = self.client.post(self.url, data={"content": "testpost"})
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(
            Tweet.objects.filter(content="testpost", user=self.user).exists()
        )

    def test_failure_post_with_empty_content(self):
        empty_content_post = {"content": ""}
        response = self.client.post(self.url, empty_content_post)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["content"], ["このフィールドは必須です。"])

    def test_failure_post_with_too_long_content(self):
        too_long_content_post = {"content": "a" * 190}
        response = self.client.post(self.url, too_long_content_post)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["content"],
            [
                "この値は 140 文字以下でなければなりません( "
                + str(len(too_long_content_post["content"]))
                + " 文字になっています)。"
            ],
        )


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        self.post = Tweet.objects.create(content="testpost", user=self.user)
        self.url = reverse("tweets:detail", kwargs={"pk": self.post.pk})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["tweet_detail"],
            self.post,
        )


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@test.com",
            password="testpassword1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@test.com",
            password="testpassword2",
        )
        self.client.login(username="testuser1", password="testpassword1")
        self.post1 = Tweet.objects.create(user=self.user1, content="testpost1")
        self.post2 = Tweet.objects.create(user=self.user2, content="testpost2")

    def test_success_post(self):
        self.url = reverse("tweets:delete", kwargs={"pk": self.post1.pk})
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(Tweet.objects.filter(content="testpost1").exists())

    def test_failure_post_with_not_exist_tweet(self):
        self.url = reverse("tweets:delete", kwargs={"pk": 123})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Tweet.objects.filter(content="testpost1").exists())

    def test_failure_post_with_incorrect_user(self):
        self.url = reverse("tweets:delete", kwargs={"pk": self.post2.pk})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Tweet.objects.filter(content="testpost2").exists())


class TestFavoriteView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_favorited_tweet(self):
        pass


class TestUnfavoriteView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_unfavorited_tweet(self):
        pass
