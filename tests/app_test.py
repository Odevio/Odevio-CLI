import re

from tests.appollo_test import AppolloTest
from tests import fixture
from appollo.commands import app


class TestAppList(AppolloTest):
    command = app.ls

    def _get_args(self, **args):
        return None

    def test_empty(self):
        self.test_contains("You did not register any apps. Create one with")

    def test_correct(self):
        self.test_table(["KEY", "Name", "Apple Name", "Bundle ID", "Account"], [
            [fixture.app_key, "AppolloTestApp", "AppolloTestApp", "space.appollo."+fixture.username, f"TestAccount ({fixture.apple_account_key})"]
        ])


class TestAppMake(AppolloTest):
    command = app.mk

    def _get_args(self, name="AppolloTestApp", bundle_id=None, account_key=None):
        if bundle_id is None:
            bundle_id = "space.appollo."+fixture.username
        if account_key is None:
            account_key = fixture.apple_account_key
        return [
            "--name", name,
            "--bundle-id", bundle_id,
            "--account-key", account_key
        ]

    def test_wrong_account(self):
        self.test("Error: for account - ['Object with key=WRONG does not exist.']", account_key="WRONG")

    def test_correct(self):
        output = self.test_contains(["Congratulations! Your application AppolloTestApp has been created in Appollo as AppolloTestApp with key \"", "\" and on the App Store as ID \""])
        fixture.app_key = re.findall("with key \"([A-Z0-9]{3})\"", output)[0]

    def test_existing_bundle_id(self):
        self.test("Error: ['This bundle ID already exists']")


class TestAppRemove(AppolloTest):
    command = app.rm

    def _get_args(self, key=None, delete_on_apple=False):
        if key is None:
            key = fixture.app_key
        args = [key]
        if delete_on_apple:
            args.append("--delete-on-apple")
        return args

    def test_wrong_key(self):
        self.test("Cannot delete something that does not exist.", key="WRONG")

    def test_correct(self):
        self.test(f"Application with key \"{fixture.app_key}\" successfully removed.")
        fixture.app_key = None

    def test_apple_correct(self):
        self.test(f"Application with key \"{fixture.app_key}\" successfully removed.", delete_on_apple=True)
        fixture.app_key = None


class TestAppImport(AppolloTest):
    command = app.import_app

    def _get_args(self, name="AppolloTestApp", bundle_id=None, account_key=None):
        if bundle_id is None:
            bundle_id = "space.appollo."+fixture.username
        if account_key is None:
            account_key = fixture.apple_account_key
        return [
            "--name", name,
            "--bundle-id", bundle_id,
            "--account-key", account_key
        ]

    def test_wrong_account(self):
        self.test("Error: for account - ['Object with key=WRONG does not exist.']", account_key="WRONG")

    def test_wrong_bundle_id(self):
        self.test("Error: for bundle_id - Bundle ID not found on your Apple Developer account.", bundle_id=f"space.appollo.{fixture.username}_wrong")

    def test_correct(self):
        output = self.test_contains(f"Congratulations! Your application AppolloTestApp has been imported on Appollo as AppolloTestApp. It is registered with key ")
        fixture.app_key = output[-6:-3]

    def test_existing(self):
        self.test("Error: ['This bundle ID already exists']")


class TestAppLink(AppolloTest):
    command = app.link

    def _get_args(self, key=None, team_key=None):
        if key is None:
            key = fixture.app_key
        if team_key is None:
            team_key = fixture.team_key
        return [key, "--team-key", team_key]

    def test_wrong_key(self):
        self.test("This application or team does not exist or you do not have access to it", key="WRONG")

    def test_wrong_team(self):
        self.test("This application or team does not exist or you do not have access to it", team_key="WRONG")

    def test_correct(self):
        self.test(f"Team \"{fixture.team_key}\" is now linked to application \"{fixture.app_key}\".")

    def test_already_linked(self):
        self.test(f"Error: The app is already included in the team through the account TestAccount ({fixture.apple_account_key})")


class TestAppUnlink(AppolloTest):
    command = app.unlink

    def _get_args(self, key=None, team_key=None):
        if key is None:
            key = fixture.app_key
        if team_key is None:
            team_key = fixture.team_key
        return [key, "--team-key", team_key]

    def test_wrong_key(self):
        self.test("Cannot delete something that does not exist.", key="WRONG")

    def test_wrong_team(self):
        self.test("Cannot delete something that does not exist.", team_key="WRONG")

    def test_correct(self):
        self.test(f"Team \"{fixture.team_key}\" is now unlinked from application \"{fixture.app_key}\".")
