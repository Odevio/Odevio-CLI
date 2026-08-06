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
@click.option('--bundle-id', help="Bundle identifier of the app to launch once the simulator is up.")
def start(key, device, bundle_id):
    """ Starts a simulator on the machine of the build with key \"KEY\".

    \f
    Booting takes a moment, and the command waits for it: a screenshot taken too early catches a black
    screen or the boot logo, which Apple accepts happily and a human reviewer refuses much later.

    Connect to the machine with :code:`odevio build connect` to see the simulator and use your app.
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/builds/", "Build", does_not_exist_msg="You have no build running.")
        if key is None:
            return
    data = {"device": device}
    if bundle_id:
        data["bundle_id"] = bundle_id
    started = api.post(f"/builds/{key}/simulator/", json_data=data)
    if started:
        console.print(f"[success]{device} is running on the build machine.[/success]")
        console.print("Connect with [code]odevio build connect[/code] to see it, open your app and go to "
                      "the screen you want to show.")
        console.print("Then take the picture with [code]odevio screenshot capture[/code].")


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
