import click

from odevio.helpers import login_required_warning_decorator


@click.group()
def screenshot():
    """ Take App Store screenshots from a simulator on an Odevio machine.

    \f
    The App Store needs screenshots, and taking them normally means owning an iPhone. These commands run
    the app in a simulator on one of our Macs instead, and photograph it there.

    The picture is taken from the simulator itself rather than from the remote desktop, so it comes out at
    exactly the pixel size Apple asks for, with no window borders and no rescaling.

    You navigate your own app during the session and say when to capture. That is deliberate: reaching
    the screens worth showing means signing in, having some data on screen and knowing where to tap, and
    nothing does that better than the person who wrote the app.

    Usage:
    """


@screenshot.command()
@login_required_warning_decorator
@click.argument('key', required=False)
def devices(key):
    """ Lists the simulators available on the machine of the build with key \"KEY\". """
    from rich.table import Table

    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/builds/", "Build", does_not_exist_msg="You have no build running.")
        if key is None:
            return
    try:
        simulators = api.get(f"/builds/{key}/simulators/")
    except api.NotFoundException:
        console.print("This key is invalid or you do not have access to it.")
        return
    if not simulators:
        return

    table = Table()
    table.add_column("Device")
    table.add_column("iOS")
    for simulator in simulators:
        table.add_row(simulator["name"], simulator["runtime"].replace("iOS-", "").replace("-", "."))
    console.print(table)


@screenshot.command()
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--device', prompt=True, help="Name of the simulator to start, as shown by 'devices'.")
@click.option('--no-app', is_flag=True, help="Only start the simulator, without building and installing.")
def start(key, device, no_app):
    """ Starts a simulator on the machine of the build with key \"KEY\", with your app on it.

    \f
    Booting takes a moment, and the command waits for it: a screenshot taken too early catches a black
    screen or the boot logo, which Apple accepts happily and a human reviewer refuses much later.

    Your app is then built for the simulator, installed and launched, which takes a few minutes.

    Connect to the machine with :code:`odevio build connect` to see the simulator and use your app.
    """
    from odevio import api
    from odevio.settings import console

    if key is None:
        from odevio.helpers import terminal_menu
        key = terminal_menu("/builds/", "Build", does_not_exist_msg="You have no build running.")
        if key is None:
            return

    started = api.post(f"/builds/{key}/simulator/", json_data={"device": device})
    if not started:
        return
    console.print(f"[success]{device} is running on the build machine.[/success]")

    if no_app:
        console.print("Install your app yourself, then take pictures with "
                      "[code]odevio screenshot capture[/code].")
        return

    console.print("Building your app for the simulator, this takes a few minutes...")
    installed = api.post(f"/builds/{key}/simulator-app/", json_data={"device": device})
    if not installed:
        return
    console.print(f"[success]{installed.get('bundle_id') or 'Your app'} is running on the "
                  f"simulator.[/success]")
    # Flutter refuses to build a simulator app in anything but debug mode, and a debug build paints a
    # DEBUG ribbon over the top right corner. Better said now than discovered on the finished pictures.
    console.print("")
    console.print("[warning]Your app will show a DEBUG ribbon in the corner.[/warning] Apple only lets "
                  "Flutter build for a simulator in debug mode, and that is what debug mode looks like.")
    console.print("Remove it by adding this as the first line of [code]main()[/code], then start again:")
    console.print("    [code]WidgetsApp.debugAllowBannerOverride = false;[/code]")
    console.print("It changes nothing for a published app: the ribbon only exists in debug builds.")
    console.print("")
    console.print("Connect with [code]odevio build connect[/code], go to the screen you want to show, "
                  "then run [code]odevio screenshot capture[/code].")


@screenshot.command()
@login_required_warning_decorator
@click.argument('key', required=False)
def capture(key):
    """ Photographs what the simulator is showing, for the build with key \"KEY\".

    \f
    Run this once per screen you want on your App Store page: navigate to a screen, capture, navigate to
    the next, capture again. Apple takes up to ten per device size and needs at least one.

    The image is kept with your app, ready to be sent to the App Store.
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/builds/", "Build", does_not_exist_msg="You have no build running.")
        if key is None:
            return
    taken = api.post(f"/builds/{key}/screenshot/", json_data={})
    if taken:
        console.print(f"[success]Captured at {taken['width']}x{taken['height']}.[/success]")
        if taken.get("display_type") is None:
            console.print("[warning]This size does not match a known App Store slot; it will be checked "
                          "against Apple when the screenshots are sent.[/warning]")
        console.print("Go to the next screen and run this again, or send them with "
                      "[code]odevio screenshot push[/code].")


@screenshot.command()
@login_required_warning_decorator
@click.argument('key', required=False)
def push(key):
    """ Sends the screenshots of the app with key \"KEY\" to its App Store page.

    \f
    Whatever is already on the App Store page for those device sizes is replaced, so the page ends up
    matching what you have here rather than holding both.
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return
    result = api.post(f"/applications/{key}/push-screenshots/", json_data={})
    if result:
        console.print(f"[success]{result['sent']} screenshot(s) sent to the App Store.[/success]")
