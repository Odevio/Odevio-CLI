import click

from odevio import settings
from odevio.helpers import login_required_warning_decorator


@click.group()
def app():
    """ Subcommands to manage your applications on Odevio. """


@app.command()
@login_required_warning_decorator
def ls():
    """ Lists the app identifiers to which the logged in user has access.

    \f
    Example output:

    .. image:: /img/odevio-ls.png
        :alt: example output of the odevio ls command
        :align: center

    Usage:
    """
    from rich.syntax import Syntax
    from rich.table import Table

    from odevio import api
    from odevio.settings import console

    apps = api.get("/applications/")

    if apps:
        table_apps = Table()
        table_apps.add_column("KEY")
        table_apps.add_column("Name")
        table_apps.add_column("Apple Name")
        table_apps.add_column("Bundle ID")
        table_apps.add_column("Account")
        for app in apps:
            table_apps.add_row(app['key'], app['name'], app['apple_name'], app['bundle_id'], app['account']['name'] + " (" + app['account']['key'] + ")")

        console.print(table_apps)
    else:
        code = Syntax(
            code="$ odevio app mk --name NAME --bundle-id BUNDLE_ID --account-key APPLE_DEVELOPER_ACCOUNT_KEY",
            lexer="shell")
        console.print(f"You did not register any app identifiers. Create one with")
        console.print(code)


@app.command()
@login_required_warning_decorator
@click.option('--name', prompt=True, help="Your app identifier name (e.g.: your app's name)")
@click.option('--bundle-id', prompt=True, help="The bundle ID for your app on Apple (e.g.: com.company.appname)")
@click.option('--account-key', prompt=False, help="Odevio key to the Apple Developer Account")
def mk(name, bundle_id, account_key):
    """ Creates a new app identifier.

    ..note: This will also create an app identifier with this bundle ID on your Developer Account. This allows us to verify the validity of your bundle ID
     """
    import textwrap

    from rich.text import Text

    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if account_key is None:
        account_key = terminal_menu("/developer-accounts/", "Developer Account",
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            No developer accounts are linked to your profile. Check out [code]$ odevio apple add [/code] to link your developer account to Odevio.
                                        """
                                    )))
        if account_key is None:
            return

    application = api.post(
        "/applications/",
        json_data={
            "name": name,
            "bundle_id": bundle_id,
            "account": account_key,
            "apple_create": True,
        }
    )

    if application:
        console.print(f"Congratulations! Your app identifier {application['apple_name']} has been created "
                      f"in Odevio as {application['name']} with key \"{application['key']}\" and on the "
                      f"App Store as ID \"{application['apple_id']}\"")


@app.command()
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--delete-on-apple', is_flag=True, help="Also delete the app identifier on Apple")
def rm(key, delete_on_apple):
    """ Deletes the app identifier with key \"KEY\" from Odevio and on Apple if specified. """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return

    url = f"/applications/{key}"
    if delete_on_apple:
        url += "?apple=1"
    account = api.delete(url)

    if account:
        console.print(f"App identifier with key \"{key}\" successfully removed.")


@app.command("link")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--team-key', prompt=False, help="Key of the team to link")
def link(key, team_key):
    """ Links an app identifier to Odevio team with key \"KEY\".

    \f
    .. warning:: All users who are in a team linked to an Apple Developer Account have full control over it.
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/?manager=me", "Application", does_not_exist_msg="You do not have any app identifier.")
        if key is None:
            return

    if team_key is None:
        team_key = terminal_menu("/teams/", "Team", does_not_exist_msg="You are not part of any team.")
        if team_key is None:
            return

    try:
        teams = api.post(f"/applications/{key}/teams/{team_key}/")
    except api.NotFoundException:
        console.print("This app identifier or team does not exist or you do not have access to it")
        return

    if teams:
        console.print(f"Team \"{team_key}\" is now linked to app identifier \"{key}\".")


@app.command("unlink")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--team-key', prompt=False, help="Key of the team to link")
def unlink(key, team_key):
    """ Links or unlinks an app identifier to Odevio team with key \"KEY\".
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/?manager=me&hasteams=1", "Application", does_not_exist_msg="You do not have any app identifiers in a team.")
        if key is None:
            return

    if team_key is None:
        team_key = terminal_menu(f"/applications/{key}/teams/", "Team", does_not_exist_msg="This app is not part of any team")
        if team_key is None:
            return

    deleted = api.delete(f"/applications/{key}/teams/{team_key}/")

    if deleted:
        console.print(f"Team \"{team_key}\" is now unlinked from app identifier \"{key}\".")


@app.command("import")
@login_required_warning_decorator
@click.option('--name', prompt=True, help="Your app identifier name (e.g.: your app's name)")
@click.option('--bundle-id', prompt=True, help="The bundle ID for your app on Apple (e.g.: com.company.appname)")
@click.option('--account-key', prompt=False, help="Odevio key to the Apple Developer Account")
def import_app(name, bundle_id, account_key):
    """ Imports an app identifier from Apple Developer to Odevio. """
    import textwrap

    from rich.text import Text

    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if account_key is None:
        account_key = terminal_menu("/developer-accounts/", "Developer Account",
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            No developer accounts are linked to your profile. Check out [code]$ odevio apple add [/code] to link your developer account to Odevio.
                                        """
                                    )))
        if account_key is None:
            return

    application = api.post(
        "/applications/",
        json_data={
            "name": name,
            "bundle_id": bundle_id,
            "account": account_key,
            "apple_create": False,
        }
    )

    if application:
        console.print(f"Congratulations! Your app identifier {application['apple_name']} has been imported on Odevio "
                      f"as {application['name']}. It is registered with key \"{application['key']}\".")

@app.command("screenshots")
@login_required_warning_decorator
@click.argument('key', required=False)
def screenshots(key):
    """ Returns a link to the screenshot editor for the app with key \"KEY\". """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return
    try:
        screenshot_link = api.get(f"/applications/{key}/screens/")
    except api.NotFoundException:
        console.print("This key is invalid or you do not have access to it.")
        return
    if screenshot_link:
        console.print("Here's the link to the screenshot editor:")
        console.print(f"[link]{settings.API_BASE_URL}{screenshot_link['url']}[/link]")
        