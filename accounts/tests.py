from django.contrib.auth import get_user_model, SESSION_KEY
from django.test import TestCase
from django.urls import reverse

from mysite import settings
from .forms import SignUpForm

CustomUser = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        user = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, user)
        self.assertTrue(
            CustomUser.objects.filter(
                username="testuser", email="test@test.com"
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        empty_user = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, empty_user)
        self.assertEqual(response.status_code, 200)
        form = SignUpForm(empty_user)
        self.assertFalse(form.is_valid())
        self.assertFalse(CustomUser.objects.exists())

    def test_failure_post_with_empty_username(self):
        username_empty_user = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, username_empty_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])
        self.assertFalse(CustomUser.objects.exists())

    def test_failure_post_with_empty_email(self):
        email_empty_user = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, email_empty_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]

        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])

        self.assertFalse(CustomUser.objects.exists())

    def test_failure_post_with_empty_password(self):
        password_empty_user = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, password_empty_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])
        self.assertFalse(CustomUser.objects.exists())

    def test_failure_post_with_duplicated_user(self):
        duplicated_user = {
            "username": "testuser",
            "email": "test2@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        response = self.client.post(self.url, duplicated_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["username"], ["同じユーザー名が既に登録済みです。"])
        self.assertFalse(
            CustomUser.objects.filter(
                username="testuser", email="test2@test.com"
            ).exists()
        )

    def test_failure_post_with_invalid_email(self):
        email_failure_user = {
            "username": "testuser",
            "email": "test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, email_failure_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["email"], ["有効なメールアドレスを入力してください。"])
        self.assertFalse(CustomUser.objects.exists())

    def test_failure_post_with_too_short_password(self):
        password_failure_user = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "short",
            "password2": "short",
        }
        response = self.client.post(self.url, password_failure_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは短すぎます。最低 8 文字以上必要です。"])
        self.assertFalse(CustomUser.objects.exists())

    def test_failure_post_with_password_similar_to_username(self):
        password_failure_user = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(self.url, password_failure_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは ユーザー名 と似すぎています。"])
        self.assertFalse(CustomUser.objects.exists())

    def test_failure_post_with_only_numbers_password(self):
        password_failure_user = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "12435678",
            "password2": "12435678",
        }
        response = self.client.post(self.url, password_failure_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは数字しか使われていません。"])
        self.assertFalse(CustomUser.objects.exists())

    def test_failure_post_with_mismatch_password(self):
        password_failure_user = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword2",
        }
        response = self.client.post(self.url, password_failure_user)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])
        self.assertFalse(CustomUser.objects.exists())


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_empty_password(self):
        pass


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )

    def test_success_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def test_success_get(self):
        pass


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
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_user(self):
        pass

    def test_failure_post_with_self(self):
        pass


class TestUnfollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowingListView(TestCase):
    def test_success_get(self):
        pass


class TestFollowerListView(TestCase):
    def test_success_get(self):
        pass
