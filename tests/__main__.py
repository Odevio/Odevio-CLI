"""
Need file fixture.py with these:
apple_id =
apple_key_id =
apple_issuer_id =
apple_key_path =
"""

import os.path
import random

import odevio.settings
import odevio.api
from tests import fixture, account_test, team_test, apple_test, app_test
from tests.odevio_test import OdevioTestFailed

assert odevio.settings.API_BASE_URL != "https://odevio.com", "Do not run test on the production environment"

fixture.username = f"test_{random.Random().randint(100000, 999999)}"
odevio.api.delete_jwt_token()

other_user_created = False


def switch_other_user():
    os.replace(odevio.settings.get_config_path(), "backup.ini")
    if not os.path.exists("other.ini"):
        odevio.api.get_authorization_header(f"{fixture.username}_other@odevio.com", "password")
    else:
        os.replace("other.ini", odevio.settings.get_config_path())


def switch_back_user():
    if not os.path.exists("backup.ini"):
        return
    os.replace(odevio.settings.get_config_path(), "other.ini")
    os.replace("backup.ini", odevio.settings.get_config_path())


try:
    # User account
    account_test.TestSignup().test_correct()
    account_test.TestSignup().test_existing_email()
    account_test.TestSignup().test_existing_username()
    account_test.TestSignout().test_correct()
    account_test.TestSignin().test_wrong_username()
    account_test.TestSignin().test_wrong_password()
    account_test.TestSignin().test_correct()
    account_test.TestProfile().test_correct()

    # Teams
    team_test.TestTeamList().test_empty()
    team_test.TestTeamMake().test_correct()
    team_test.TestTeamList().test_correct()
    odevio.api.post('/register/', authorization=False, json_data={
        "email": f"{fixture.username}_other@odevio.com",
        "password": "password",
        "username": f"{fixture.username}_other"
    })
    other_user_created = True
    team_test.TestTeamAddUser().test_wrong_team()
    team_test.TestTeamAddUser().test_wrong_username()
    team_test.TestTeamAddUser().test_correct()
    team_test.TestTeamList().test_correct(members=[fixture.username, fixture.username+"_other"])
    switch_other_user()
    account_test.TestProfile().test_correct(username=fixture.username+"_other")
    team_test.TestTeamList().test_correct(members=[fixture.username, fixture.username+"_other"])
    team_test.TestTeamRemoveUser().test_remove_admin()
    team_test.TestTeamDelete().test_unauthorized()
    switch_back_user()

    # Apple account
    apple_test.TestAppleList().test_empty()
    apple_test.TestAppleAdd().test_wrong_key_id()
    apple_test.TestAppleAdd().test_wrong_issuer_id()
    apple_test.TestAppleAdd().test_wrong_private_key()
    apple_test.TestAppleAdd().test_correct()
    apple_test.TestAppleAdd().test_existing()
    apple_test.TestAppleList().test_correct()
    apple_test.TestAppleDetail().test_correct()
    apple_test.TestAppleDetail().test_wrong_key()
    apple_test.TestAppleUpdate().test_correct(apple_id="ChangedID", name="ChangedName")
    apple_test.TestAppleDetail().test_correct(apple_id="ChangedID", name="ChangedName")
    apple_test.TestAppleUpdate().test_correct()
    apple_test.TestAppleDetail().test_correct()
    apple_test.TestAppleRefreshDevices().test_wrong_key()
    apple_test.TestAppleRefreshDevices().test_quiet()
    apple_test.TestAppleRefreshDevices().test_list()

    # Apps
    app_test.TestAppList().test_empty()
    app_test.TestAppMake().test_wrong_account()
    app_test.TestAppMake().test_correct()
    app_test.TestAppMake().test_existing_bundle_id()
    app_test.TestAppList().test_correct()
    app_test.TestAppRemove().test_wrong_key()
    app_test.TestAppRemove().test_correct()
    app_test.TestAppImport().test_wrong_account()
    app_test.TestAppImport().test_wrong_bundle_id()
    app_test.TestAppImport().test_correct()
    app_test.TestAppImport().test_existing()
    app_test.TestAppList().test_correct()
    app_test.TestAppLink().test_wrong_key()
    app_test.TestAppLink().test_wrong_team()
    app_test.TestAppLink().test_correct()
    team_test.TestTeamList().test_correct(
        members=[fixture.username, fixture.username+"_other"],
        applications=[{'key': fixture.app_key, 'name': "OdevioTestApp", 'bundle_id': "com.odevio."+fixture.username}]
    )
    switch_other_user()
    app_test.TestAppList().test_correct()
    switch_back_user()
    app_test.TestAppUnlink().test_wrong_key()
    app_test.TestAppUnlink().test_wrong_team()
    app_test.TestAppUnlink().test_correct()
    team_test.TestTeamList().test_correct(members=[fixture.username, fixture.username+"_other"])
    switch_other_user()
    app_test.TestAppList().test_empty()
    switch_back_user()

    # Apple account link
    apple_test.TestAppleLink().test_wrong_key()
    apple_test.TestAppleLink().test_wrong_team()
    apple_test.TestAppleLink().test_correct()
    team_test.TestTeamList().test_correct(
        members=[fixture.username, fixture.username+"_other"],
        accounts=[{'key': fixture.apple_account_key, 'name': "TestAccount", 'manager': fixture.username}]
    )
    apple_test.TestAppleLink().test_again()
    switch_other_user()
    apple_test.TestAppleList().test_correct()
    apple_test.TestAppleDetail().test_correct()
    apple_test.TestAppleDelete().test_unauthorized()
    app_test.TestAppList().test_correct()
    switch_back_user()
    app_test.TestAppLink().test_already_linked()
    apple_test.TestAppleUnlink().test_wrong_key()
    apple_test.TestAppleUnlink().test_wrong_team()
    apple_test.TestAppleUnlink().test_correct()
    team_test.TestTeamList().test_correct(members=[fixture.username, fixture.username+"_other"])
    apple_test.TestAppleUnlink().test_again()
    switch_other_user()
    apple_test.TestAppleList().test_empty()
    switch_back_user()

    # Removals
    app_test.TestAppRemove().test_apple_correct()
    apple_test.TestAppleDelete().test_wrong_key()
    apple_test.TestAppleDelete().test_correct()
    team_test.TestTeamRemoveUser().test_wrong_team()
    team_test.TestTeamRemoveUser().test_wrong_username()
    team_test.TestTeamRemoveUser().test_correct()
    team_test.TestTeamList().test_correct()
    team_test.TestTeamDelete().test_wrong_team()
    team_test.TestTeamDelete().test_correct()
    team_test.TestTeamList().test_empty()

    print("\u001b[32mAll tests passed\u001b[0m")

except OdevioTestFailed as e:
    print(e)

finally:
    print("Cleaning test data...")
    switch_back_user()
    if hasattr(fixture, "team_key") and fixture.team_key:
        odevio.api.delete(f"/teams/{fixture.team_key}")
        print("Deleted test team")
    if hasattr(fixture, "app_key") and fixture.app_key:
        odevio.api.delete(f"/applications/{fixture.app_key}?apple=1")
        print("Deleted test app")
    if hasattr(fixture, "apple_account_key") and fixture.apple_account_key:
        odevio.api.delete(f"/developer-accounts/{fixture.apple_account_key}")
        print("Deleted test Apple account")
    odevio.api.delete('/my-account/')  # Delete all test data
    print("Deleted test user")
    odevio.api.delete_jwt_token()
    if other_user_created:
        odevio.api.get_authorization_header(f"{fixture.username}_other@odevio.com", "password")
        odevio.api.delete('/my-account/')
        odevio.api.delete_jwt_token()
        print("Deleted other test user")
    try:
        os.remove("backup.ini")
    except FileNotFoundError:
        pass
    try:
        os.remove("other.ini")
    except FileNotFoundError:
        pass
