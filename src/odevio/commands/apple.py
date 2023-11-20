import click

from odevio.helpers import login_required_warning_decorator, terminal_menu


@click.group("apple")
def apple():
    """ Subcommands to manage Apple specific settings for Odevio.

    Access to an Apple developer account makes it possible for Odevio to retrieve and/or create all information
    necessary to create a build of your application that you will be able to publish on the app store.

    \f

    A number of Apple specific objects is linked to each developer account and make it possible for Odevio to build
    iOS apps :

        - **Certificates** : The certificates resource represents the digital certificates you use to sign your iOS or Mac apps for development and distribution. *These are managed automatically by Odevio.*

        - **Profiles** : A provisioning profile is a collection of digital entities that uniquely ties developers and devices to an authorized iPhone Development Team and enables a device to be used for testing. *These are managed automatically by Odevio.*

        - **Identifiers** : Uniquely identifies your app throughout the Apple eco-system. *These are imported or created in Odevio through command : $ odevio app*

        - **Devices** : List of devices on which you want to be able to test your builds prior to release on the App Store. At least one device should be added to the device list for Odevio to be able to build apps.

    These can be added, modified or deleted through |https://developers.apple.com|.

    \f

    .. danger:: Deletion or modification of Certificates, Profiles or Identifiers managed by Odevio through |https://developers.apple.com| may break Odevio.

    .. |https://developers.apple.com| raw:: html

       <a href="https://developers.apple.com" target="_blank">https://developers.apple.com</a>

    Usage :
    """
    pass


@apple.command("detail")
@login_required_warning_decorator
@click.argument('key', required=False)
def developer_account_detail(key):
    """ Gets detailed information about your Apple Developer Account with key \"KEY\" on Odevio.

    Returned information :

        - General information

        - Devices

        - Certificates

        - Provisioning profiles

    \f

    .. note:: Odevio updates Apple Developer Account information automatically when starting a build with Odevio.

    Example output :

    .. image:: /img/odevio-apple-detail.png
        :alt: example output of the odevio team ls command
        :align: center

    Usage :

    """
    from rich.text import Text
    from rich.panel import Panel
    from rich.table import Table
    import textwrap

    from odevio import api
    from odevio.settings import console
    from odevio.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/developer-accounts/", "Developer account",
                                does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                    f"""
                                            You have no Apple developer accounts setup with Odevio. Check out [code]$ odevio apple add [/code] to add one.
                                        """
                                )))
        if key is None:
            return

    try:
        dev_account = api.get(f"/developer-accounts/{key}/")
    except api.NotFoundException:
        console.print("There is no developer account with this key")
        return
    provisioning_profiles = api.get(f"/developer-accounts/{key}/provisioning-profiles/")

    if dev_account:
        console.print(Panel(Text.from_markup(
            f"""
            Odevio Key : [bold]{dev_account["key"]}[/bold]
            Name : [bold]{dev_account["name"]}[/bold]
            Team ID : [bold]{dev_account["apple_id"]}[/bold]
            Apple API Key ID : [bold]{dev_account["api_key_id"]}[/bold]
            Admin : [bold]{dev_account["manager"]}[/bold]
            """
        ), title="Apple Developer Account"))

    if len(dev_account['apple_account_devices']) > 0:
        table_devices = Table(expand=True, title="Devices in your Apple Developer Account registered on Odevio.")
        table_devices.add_column("Name")
        table_devices.add_column("Identifier/Device UDID")
        table_devices.add_column("Type")
        for device in dev_account['apple_account_devices']:
            table_devices.add_row(device['name'], device['device_udid'], device['device_class'])
        console.print(table_devices)

    if len(dev_account['apple_account_certificates']) > 0:
        table_cert = Table(expand=True, title="Certificates in your Apple Developer Account registered on Odevio.")
        table_cert.add_column("Name")
        table_cert.add_column("Type")
        table_cert.add_column("Expiration date")
        for cert in dev_account['apple_account_certificates']:
            table_cert.add_row(cert['apple_display_name'], cert['certificate_type'], cert['expiration_date'])
        console.print(table_cert)

    if len(provisioning_profiles) > 0:
        table_pp = Table(expand=True, title="Provisioning profiles in your Apple Developer Account registered on "
                                            "Odevio.")
        table_pp.add_column("Name")
        table_pp.add_column("Apple Name")
        table_pp.add_column("Application")
        table_pp.add_column("Expiration date")
        for pp in provisioning_profiles:
            table_pp.add_row(pp['name'], pp['apple_name'], pp['application'], pp['expiration_date'],)
        console.print(table_pp)

    console.print("Odevio updates these informations automatically when starting à build with Odevio")


@apple.command("ls")
@login_required_warning_decorator
def developer_account_ls():
    """ Lists Apple Developer Accounts to which you have access.

    \f

    Example output :

    .. image:: /img/odevio-apple-ls.png
        :alt: example output of the odevio apple ls command
        :align: center

    Usage :

    """
    from rich.table import Table

    from odevio import api
    from odevio.settings import console

    developer_accounts = api.get("/developer-accounts/")

    if len(developer_accounts) > 0:
        table = Table(title="Apple Developer Accounts you have access to")
        table.add_column("KEY")
        table.add_column("Name")
        table.add_column("Admin")
        table.add_column("Team ID")
        table.add_column("Apple API Key ID")
        for da in developer_accounts:
            table.add_row(da['key'], da['name'], da['manager'], da['apple_id'], da['api_key_id'])

        console.print(table)

        console.print("Check out [code]$ odevio apple --help[/code] to know what part of the Apple Developer Account "
                      "is used by Odevio or check related documentation at "
                      "[link]https://odevio.readthedocs.io/en/master/reference_guide/index.html#odevio-apple[/link].")
    else:
        console.print('You do not have access to a developer account with Odevio.')


@apple.command("add")
@login_required_warning_decorator
@click.option("--apple-id", required=True, prompt=True, help="ID of your developer account on Apple")
@click.option('--name', prompt=True, help="A user friendly name for Odevio")
@click.option('--key-id', required=True, prompt=True, help="API key \"Key ID\" on App Store Connect")
@click.option('--issuer-id', required=True, prompt=True, help="Issuer ID on App Store Connect")
@click.option('--private-key', required=True, prompt=True,
              type=click.Path(exists=True, resolve_path=True, file_okay=True, dir_okay=False),
              help="Path to the private key downloaded from App Store Connect")
@click.option('--team', multiple=True, help="Key of the team to add the account to. Can be specified multiple times")
def developer_account_add(apple_id, key_id, issuer_id, private_key, team, name=None):
    """ Add access to an Apple developer account for Odevio.

    \f
    .. warning:: Once the developer account has been created there is no way to retrieve the private key from Odevio.
    .. note:: We have no way to verify your developer account's ID on Apple. In case of error, your builds will fail.
    """
    from odevio import api
    from odevio.settings import console
    import os.path

    account = api.post(
        "/developer-accounts/",
        json_data={
            "name": name,
            "apple_id": apple_id,
            "api_key_id": key_id,
            "api_issuer_id": issuer_id,
            "teams": team,
        },
        files={
            "api_private_key": open(os.path.expanduser(private_key), "rb"),
        }
    )

    if account:
        console.print(f"Linked Odevio to the Apple developer account \"{account['name']}\" successfully. It has key {account['key']}")


@apple.command("edit")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option("--apple-id", help="ID of your developer account on Apple")
@click.option('--name', help="A user friendly name for Odevio")
def developer_account_edit(key, apple_id=None, name=None):
    """ Edit properties of a developer account linked to Odevio.

    \f
    .. note:: We have no way to verify your developer account's ID on Apple. In case of error, your builds will fail.
    """
    from odevio import api
    from odevio.settings import console
    from rich.text import Text
    import textwrap

    if key is None:
        key = terminal_menu("/developer-accounts/", "Developer account",
                            does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                f"""
                                            You have no Apple developer accounts setup with Odevio. Check out [code]$ odevio apple add [/code] to add one.
                                        """
                            )))
        if key is None:
            return

    account = api.put(
        f"/developer-accounts/{key}/",
        json_data={
            "name": name,
            "apple_id": apple_id,
        },
    )

    if account:
        console.print(f"Account {key} has been successfully modified.")


@apple.command("rm")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.confirmation_option(prompt="Everything related to this Developer Account will be deleted. Are you sure you want to do this ?")
def developer_account_rm(key):
    """ Removes access to Apple Developer account with key \"KEY\" for Odevio.

    This does not remove the Apple Developer account from Apple, it only removes the link between Odevio and Apple.

    \f
    ..note::
        This will also remove every application, every build, every devices, every certificate, every profile and every
        objects related to that Apple Developer account on Odevio (it will not remove these from Apple).
    """
    from odevio import api
    from odevio.settings import console
    from rich.text import Text
    import textwrap

    if key is None:
        key = terminal_menu("/developer-accounts/?manager=me", "Developer account",
                            does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                f"""
                                            You have no Apple developer accounts setup with Odevio. Check out [code]$ odevio apple add [/code] to add one.
                                        """
                            )))
        if key is None:
            return

    api.delete(f"/developer-accounts/{key}", json_decode=False)
    console.print(f"Removed Apple developer account with Odevio key \"{key}\" successfully.")


@apple.command("link")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--team-key', help="Key of the team to link")
def link(key, team_key):
    """ Links the developer account with key \"KEY\" to an Odevio team.

    \f

    By default a newly added Apple Developer Account created on Odevio is only linked to the user having created it.
    When using this command you can link the Apple Developer Account directly to one of your teams on Odevio
    giving full access to your team members.

    .. warning:: All users who are in a team linked to an Apple Developer Account have full control over it.

    .. note:: Once the developer account has been created, there is no way to retrieve the private key from Odevio.
              Making it impossible for team members to "steal" your Apple Developer account.
    """
    from odevio import api
    from odevio.settings import console
    from odevio.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/developer-accounts/?manager=me", "Developer account",
                            does_not_exist_msg="You are not the manager of any apple developer accounts")
        if key is None:
            return

    if team_key is None:
        team_key = terminal_menu("/teams/", "Team", does_not_exist_msg="You are not part of any teams")
        if team_key is None:
            return

    try:
        api.post(f"/developer-accounts/{key}/teams/{team_key}/")
        console.print(f"Team \"{team_key}\" is now linked to "
                      f"Apple Developer Account \"{key}\".")
    except api.NotFoundException:
        console.print("The provided account or team does not exist or you do not have access to it")


@apple.command("unlink")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--team-key', help="Key of the team to unlink")
def unlink(key, team_key):
    """ Unlinks the developer account with key \"KEY\" from an Odevio team.
    """
    from odevio import api
    from odevio.settings import console
    from odevio.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/developer-accounts/?manager=me&hasteams=1", "Apple account",
                            does_not_exist_msg="You do not have any apple developer accounts in a team")
        if key is None:
            return

    if team_key is None:
        team_key = terminal_menu(f"/developer-accounts/{key}/teams/", "Team", does_not_exist_msg="This developer account isn't shared with any team")
        if team_key is None:
            return

    deleted = api.delete(f"/developer-accounts/{key}/teams/{team_key}/")
    if deleted:
        console.print(f"Team \"{team_key}\" is now unlinked from "
                      f"Apple Developer Account \"{key}\".")


@apple.command("refresh-devices")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option("--quiet", "-q", is_flag=True, help="Flag to know if the refreshed list of devices should be hidden or not")
def refresh_devices(key, quiet):
    """
    Synchronizes the list of devices on Odevio with the Apple Developer account

    \f
    This command is used when you have just added or removed a new device from your Apple Developer account and you need it on Odevio.

    .. note: By default, this process is done each time you launch a build except if you have already made this process in the last few hours.
    """
    from rich.table import Table

    from odevio import api
    from odevio.settings import console
    from odevio.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/developer-accounts/", "Apple account",
                            does_not_exist_msg="You do not have any apple developer accounts")
        if key is None:
            return

    try:
        devices = api.get(f"/developer-accounts/{key}/refresh-devices/")
    except api.NotFoundException:
        console.print("There is no developer account with this key")
        return
    if devices:
        console.print("Your device list has been updated.")

        if not quiet:
            table = Table()
            table.add_column("Apple ID")
            table.add_column("Class")
            table.add_column("Name")

            for device in devices:
                table.add_row(device['apple_id'], device['device_class'], device['name'])

            console.print(table)
