from tests.odevio_test import OdevioTest
from tests import fixture
from odevio.commands import team


class TestTeamList(OdevioTest):
    command = team.ls

    def _get_args(self, **args):
        return None

    def test_empty(self):
        self.test_contains("You are not part of any teams. Create one with")

    def test_correct(self, key=None, name="TestTeam", admin_username=None, admin_email=None, members=None, applications=None, accounts=None):
        if key is None:
            key = fixture.team_key
        if admin_username is None:
            admin_username = fixture.username
        if admin_email is None:
            admin_email = f"{admin_username}@odevio.com"
        if members is None:
            members = [fixture.username]
        if applications is None:
            applications = []
        if accounts is None:
            accounts = []
        team_tree = [
                f"Admin username : {admin_username}",
                f"Admin email : {admin_email}",
                ("Members", members)
            ]
        if len(applications):
            team_tree.append(("Applications", [f"{app['key']} | {app['name']} | {app['bundle_id']}" for app in applications]))
        if len(accounts):
            team_tree.append(("Apple Developer Accounts", [f"{account['key']} | {account['name']} | {account['manager']}" for account in accounts]))
        self.test_tree(("My teams", [
            (f"{key} {name}", team_tree)
        ]))


class TestTeamMake(OdevioTest):
    command = team.mk

    def _get_args(self, name="TestTeam"):
        return ["--name", name]

    def test_correct(self):
        output = self.test_contains("Created team TestTeam successfully. It has key ")
        fixture.team_key = output[-4:-1]


class TestTeamAddUser(OdevioTest):
    command = team.add_member

    def _get_args(self, key=None, username=None):
        if key is None:
            key = fixture.team_key
        if username is None:
            username = f"{fixture.username}_other"
        return [key, "--username", username]

    def test_wrong_team(self):
        self.test("Team or username not found", key="WRONG")

    def test_wrong_username(self):
        self.test("Team or username not found", username=f"{fixture.username}_wrong")

    def test_correct(self):
        self.test_tree(("TestTeam", [
            f"Admin username : {fixture.username}",
            f"Admin email : {fixture.username}@odevio.com",
            ("Members", [fixture.username, f"{fixture.username}_other"])
        ]))


class TestTeamRemoveUser(OdevioTest):
    command = team.rm_member

    def _get_args(self, key=None, username=None):
        if key is None:
            key = fixture.team_key
        if username is None:
            username = f"{fixture.username}_other"
        return [key, "--username", username]

    def test_wrong_team(self):
        self.test("Cannot delete something that does not exist.", key="WRONG")

    def test_wrong_username(self):
        self.test("Cannot delete something that does not exist.", username=f"{fixture.username}_wrong")

    def test_correct(self):
        self.test(f"User {fixture.username}_other successfully removed from team {fixture.team_key}")

    def test_remove_admin(self):
        self.test("Error: You cannot remove the admin of the team.", username=fixture.username)


class TestTeamDelete(OdevioTest):
    command = team.rm

    def _get_args(self, key=None):
        if key is None:
            key = fixture.team_key
        return [key, "--yes"]

    def test_wrong_team(self):
        self.test("Cannot delete something that does not exist.", key="WRONG")

    def test_correct(self):
        self.test(f"deleted team \"{fixture.team_key}\" successfully.")
        fixture.team_key = None

    def test_unauthorized(self):
        self.test("Error: You are not allowed to delete teams for which you are not the admin.")
