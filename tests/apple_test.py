import os

from tests.odevio_test import OdevioTest
from tests import fixture
from odevio.commands import apple


class TestAppleAdd(OdevioTest):
    command = apple.developer_account_add

    def _get_args(self,
                  apple_id=fixture.apple_id,
                  name="TestAccount",
                  key_id=fixture.apple_key_id,
                  issuer_id=fixture.apple_issuer_id,
                  private_key=fixture.apple_key_path):
        return [
            "--apple-id", apple_id,
            "--name", name,
            "--key-id", key_id,
            "--issuer-id", issuer_id,
            "--private-key", private_key
        ]

    def test_wrong_key_id(self):
        self.test("Error: The provided combination of Key ID, Issuer ID and Private key is not valid", key_id="WRONG")

    def test_wrong_issuer_id(self):
        self.test("Error: The provided combination of Key ID, Issuer ID and Private key is not valid", issuer_id="WRONG")

    def test_wrong_private_key(self):
        with open("wrong_key.p8", "w") as f:
            f.write("WRONG")
        try:
            self.test("Error: for api_private_key - Invalid private key format", private_key="wrong_key.p8")
        finally:
            os.remove("wrong_key.p8")

    def test_correct(self):
        output = self.test_contains("Linked Odevio to the Apple developer account \"TestAccount\" successfully. It has key ")
        fixture.apple_account_key = output[-4:-1]

    def test_existing(self):
        self.test("Error: for api_key_id - ['developer account with this App Store Connect API key ID already exists.']")


class TestAppleList(OdevioTest):
    command = apple.developer_account_ls

    def _get_args(self, **args):
        return None

    def test_empty(self):
        self.test("You do not have access to a developer account with Odevio.")

    def test_correct(self):
        self.test_table(["KEY", "Name", "Admin", "Apple ID", "Apple API Key ID"], [
                            [fixture.apple_account_key, "TestAccount", fixture.username, fixture.apple_id, fixture.apple_key_id]
                        ], "Apple Developer Accounts you have access to", True)


class TestAppleDetail(OdevioTest):
    command = apple.developer_account_detail

    def _get_args(self, key):
        return [key]

    def test_correct(self, name="TestAccount", apple_id=fixture.apple_id):
        self.test_contains([
            f"Odevio Key : {fixture.apple_account_key}",
            f"Name : {name}",
            f"Apple ID : {apple_id}",
            f"Apple API Key ID : {fixture.apple_key_id}",
            f"Admin : {fixture.username}"
        ], key=fixture.apple_account_key)

    def test_wrong_key(self):
        self.test("There is no developer account with this key", key="WRONG")


class TestAppleUpdate(OdevioTest):
    command = apple.developer_account_edit

    def _get_args(self, key=None, apple_id=fixture.apple_key_id, name="TestAccount"):
        if key is None:
            key = fixture.apple_account_key
        return [
            key,
            "--apple-id", apple_id,
            "--name", name
        ]

    def test_correct(self, apple_id=fixture.apple_id, name="TestAccount"):
        self.test(f"Account {fixture.apple_account_key} has been successfully modified.", apple_id=apple_id, name=name)


class TestAppleLink(OdevioTest):
    command = apple.link

    def _get_args(self, key=None, team_key=None):
        if key is None:
            key = fixture.apple_account_key
        if team_key is None:
            team_key = fixture.team_key
        return [
            key,
            "--team-key", team_key
        ]

    def test_wrong_key(self):
        self.test("The provided account or team does not exist or you do not have access to it", key="WRONG")

    def test_wrong_team(self):
        self.test("The provided account or team does not exist or you do not have access to it", team_key="WRONG")

    def test_correct(self):
        self.test(f"Team \"{fixture.team_key}\" is now linked to Apple Developer Account \"{fixture.apple_account_key}\".")

    def test_again(self):
        self.test(f"Team \"{fixture.team_key}\" is now linked to Apple Developer Account \"{fixture.apple_account_key}\".")


class TestAppleUnlink(OdevioTest):
    command = apple.unlink

    def _get_args(self, key=None, team_key=None):
        if key is None:
            key = fixture.apple_account_key
        if team_key is None:
            team_key = fixture.team_key
        return [
            key,
            "--team-key", team_key
        ]

    def test_wrong_key(self):
        self.test("Cannot delete something that does not exist.", key="WRONG")

    def test_wrong_team(self):
        self.test("Cannot delete something that does not exist.", team_key="WRONG")

    def test_correct(self):
        self.test(f"Team \"{fixture.team_key}\" is now unlinked from Apple Developer Account \"{fixture.apple_account_key}\".")

    def test_again(self):
        self.test("Cannot delete something that does not exist.")


class TestAppleRefreshDevices(OdevioTest):
    command = apple.refresh_devices

    def _get_args(self, key=None, quiet=False):
        if key is None:
            key = fixture.apple_account_key
        args = [key]
        if quiet:
            args.append("-q")
        return args

    def test_wrong_key(self):
        self.test("There is no developer account with this key", key="WRONG")

    def test_quiet(self):
        self.test("Your device list has been updated.", quiet=True)

    def test_list(self):
        self.test_contains(["Your device list has been updated.", "Apple ID", "Class", "Name"])


class TestAppleDelete(OdevioTest):
    command = apple.developer_account_rm

    def _get_args(self, key=None):
        if key is None:
            key = fixture.apple_account_key
        return [key, "--yes"]

    def test_wrong_key(self):
        self.test("Cannot delete something that does not exist.", key="WRONG")

    def test_correct(self):
        self.test(f"Removed Apple developer account with Odevio key \"{fixture.apple_account_key}\" successfully.")
        fixture.apple_account_key = None

    def test_unauthorized(self):
        self.test("Error: You are not allowed to delete developer accounts for which you are not the admin.")
