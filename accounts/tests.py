from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

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
            reverse("acconts:home"),
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
        pass

    def test_failure_post_with_empty_email(self):
        pass

    def test_failure_post_with_empty_password(self):
        pass

    def test_failure_post_with_duplicated_user(self):
        pass

    def test_failure_post_with_invalid_email(self):
        pass

    def test_failure_post_with_too_short_password(self):
        pass

    def test_failure_post_with_password_similar_to_username(self):
        pass

    def test_failure_post_with_only_numbers_password(self):
        pass

    def test_failure_post_with_mismatch_password(self):
        pass


class TestLoginView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_empty_password(self):
        pass


class TestLogoutView(TestCase):
    def test_success_get(self):
        pass


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
