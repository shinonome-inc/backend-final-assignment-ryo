from django.contrib.auth import get_user_model, SESSION_KEY
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from mysite import settings

from accounts.models import FriendShip
from tweets.models import Tweet

User = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.assertFalse(User.objects.exists())
        response = self.client.post(self.url, user_data)
        self.assertTrue(
            User.objects.filter(username="testuser", email="test@test.com").exists()
        )
        self.assertEqual(User.objects.all().count(), 1)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        empty_user_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, empty_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.exists())

    def test_failure_post_with_empty_username(self):
        username_empty_user_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, username_empty_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])
        self.assertFalse(User.objects.exists())

    def test_failure_post_with_empty_email(self):
        email_empty_user_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, email_empty_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]

        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])

        self.assertFalse(User.objects.exists())

    def test_failure_post_with_empty_password(self):
        password_empty_user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, password_empty_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])
        self.assertFalse(User.objects.exists())

    def test_failure_post_with_duplicated_user(self):
        duplicated_user_data = {
            "username": "testuser",
            "email": "test2@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        response = self.client.post(self.url, duplicated_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["username"], ["同じユーザー名が既に登録済みです。"])
        self.assertFalse(
            User.objects.filter(username="testuser", email="test2@test.com").exists()
        )

    def test_failure_post_with_invalid_email(self):
        email_failure_user_data = {
            "username": "testuser",
            "email": "test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, email_failure_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["email"], ["有効なメールアドレスを入力してください。"])
        self.assertFalse(User.objects.exists())

    def test_failure_post_with_too_short_password(self):
        password_failure_user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "short",
            "password2": "short",
        }
        response = self.client.post(self.url, password_failure_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは短すぎます。最低 8 文字以上必要です。"])
        self.assertFalse(User.objects.exists())

    def test_failure_post_with_password_similar_to_username(self):
        password_failure_user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(self.url, password_failure_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは ユーザー名 と似すぎています。"])
        self.assertFalse(User.objects.exists())

    def test_failure_post_with_only_numbers_password(self):
        password_failure_user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "12435678",
            "password2": "12435678",
        }
        response = self.client.post(self.url, password_failure_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは数字しか使われていません。"])
        self.assertFalse(User.objects.exists())

    def test_failure_post_with_mismatch_password(self):
        password_failure_user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword2",
        }
        response = self.client.post(self.url, password_failure_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])
        self.assertFalse(User.objects.exists())


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        user_data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.url, user_data)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )

        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        not_exist_user_data = {
            "username": "fakeuser",
            "password": "fakepassward",
        }
        response = self.client.post(self.url, not_exist_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。",
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        password_empty_user_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, password_empty_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password"], ["このフィールドは必須です。"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
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
        self.post = Tweet.objects.create(user=self.user1, content="testpost")
        self.url = reverse(
            "accounts:user_profile", kwargs={"username": self.user1.username}
        )
        self.post1 = Tweet.objects.create(user=self.user1, content="testpost1")
        self.post2 = Tweet.objects.create(user=self.user2, content="testpost2")
        FriendShip.objects.create(followed=self.user1, following=self.user2)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertQuerysetEqual(
            response.context["tweet_list"],
            Tweet.objects.filter(user=self.user1).order_by("-created_at"),
        )
        self.assertEqual(
            response.context["followings_num"],
            FriendShip.objects.filter(followed=self.user1).count(),
        )
        self.assertEqual(
            response.context["followers_num"],
            FriendShip.objects.filter(following=self.user1).count(),
        )


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
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

    def test_success_post(self):
        self.url = reverse("accounts:follow", kwargs={"username": self.user2.username})
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(
            FriendShip.objects.filter(
                followed=self.user1, following=self.user2
            ).exists()
        )

    def test_failure_post_with_not_exist_user(self):
        self.url = reverse("accounts:follow", kwargs={"username": "unknown"})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(FriendShip.objects.exists())

    def test_failure_post_with_self(self):
        self.url = reverse("accounts:follow", kwargs={"username": self.user1.username})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(FriendShip.objects.exists())
        messages = list(get_messages(response.wsgi_request))
        message = str(messages[0])
        self.assertEqual(message, "自分自身はフォローできません。")


class TestUnfollowView(TestCase):
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
        FriendShip.objects.create(followed=self.user1, following=self.user2)

    def test_success_post(self):
        self.url = reverse(
            "accounts:unfollow", kwargs={"username": self.user2.username}
        )
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FriendShip.objects.exists())

    def test_failure_post_with_not_exist_tweet(self):
        self.url = reverse("accounts:follow", kwargs={"username": "unknown"})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            FriendShip.objects.filter(
                followed=self.user1, following=self.user2
            ).exists()
        )

    def test_failure_post_with_incorrect_user(self):
        self.url = reverse(
            "accounts:unfollow", kwargs={"username": self.user1.username}
        )
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        message = str(messages[0])
        self.assertEquals(message, "無効な操作です。")
        self.assertTrue(
            FriendShip.objects.filter(
                followed=self.user1, following=self.user2
            ).exists()
        )


class TestFollowingListView(TestCase):
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
        FriendShip.objects.create(followed=self.user2, following=self.user1)
        self.url = reverse(
            "accounts:following_list", kwargs={"username": self.user1.username}
        )

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/following_list.html")


class TestFollowerListView(TestCase):
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
        FriendShip.objects.create(followed=self.user1, following=self.user2)
        self.url = reverse(
            "accounts:follower_list", kwargs={"username": self.user1.username}
        )

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/follower_list.html")
