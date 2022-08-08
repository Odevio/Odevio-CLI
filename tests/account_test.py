from tests import fixture
from tests.appollo_test import AppolloTest
from appollo.commands import user


class TestSignup(AppolloTest):
    command = user.signup

    def _get_args(self, username=None, email=None):
        if username is None:
            username = fixture.username
        if email is None:
            email = f"{fixture.username}@appollo.space"
        return [
            "--email", email,
            "--username", username,
            "--password", "password"
        ]

    def test_correct(self):
        self.test(f"Welcome to Appollo {fixture.username}")

    def test_existing_email(self):
        self.test("Error: for email - ['user with this email address already exists.']", username=fixture.username+"_other")

    def test_existing_username(self):
        self.test("Error: for username - ['user with this Username already exists.']", email=f"{fixture.username}_other@appollo.space")


class TestSignout(AppolloTest):
    command = user.signout

    def _get_args(self, **args):
        return None

    def test_correct(self):
        self.test("You have been disconnected. See you soon...")


class TestSignin(AppolloTest):
    command = user.signin

    def _get_args(self, username=None, password="password"):
        if username is None:
            username = fixture.username
        return [
            "--email", f"{username}@appollo.space",
            "--password", password
        ]

    def test_wrong_username(self):
        self.test("Error: ['Unable to log in with provided credentials.']", username=fixture.username+"2")

    def test_wrong_password(self):
        self.test("Error: ['Unable to log in with provided credentials.']", password="wrong")

    def test_correct(self):
        self.test(f"Welcome back to Appollo {fixture.username}")


class TestProfile(AppolloTest):
    command = user.profile

    def _get_args(self, **args):
        return None

    def test_correct(self, username=None):
        if username is None:
            username = fixture.username
        self.test_contains([f"Username : {username}", f"E-mail : {username}@appollo.space"])
