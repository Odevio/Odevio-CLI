import click

from odevio.helpers import login_required_warning_decorator


def _device_memory_path(key):
    """ Where the simulator chosen for a build is remembered between commands.

    Kept beside the other Odevio settings rather than in the project, since it describes a running
    machine rather than anything belonging to the code.
    """
    import os

    from odevio.settings import get_config_path

    return os.path.join(os.path.dirname(get_config_path()), f"simulator-{key}")


def _remember_device(key, device):
    import os

    path = _device_memory_path(key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as memory:
        memory.write(device)


def _remembered_device(key):
    try:
        with open(_device_memory_path(key)) as memory:
            return memory.read().strip() or None
    except OSError:
        return None


class _KeyCheckedGroup(click.Group):
    """ Every screenshot command takes a key: an unknown one gets a sentence, not a traceback. """

    def invoke(self, ctx):
        from odevio import api

        try:
            return super().invoke(ctx)
        except api.NotFoundException:
            from odevio.settings import console
            console.print("This key is invalid or you do not have access to it.")


@click.group(cls=_KeyCheckedGroup)
def screenshot():
    """ App Store screenshots: add them, compose marketing visuals over them, send them to Apple.

    \f
    Screenshots belong to an app, or to a store listing (see :code:`odevio screenshot listing`) when there
    is no app or Apple account yet. Upload raw captures or finished pictures, compose a marketing visual
    over a capture with :code:`visual`, look at it with :code:`preview`, approve it, and
    :code:`push` sends the set to Apple.

    Without an iPhone at hand, :code:`start` and :code:`capture` run the app in a simulator on one of
    our Macs and photograph it there.

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
@click.option('--device', help="Simulator to start, as named by 'devices'. Chosen for you if omitted.")
@click.option('--ipad', is_flag=True, help="Choose an iPad rather than an iPhone.")
@click.option('--no-app', is_flag=True, help="Only start the simulator, without building and installing.")
def start(key, device, ipad, no_app):
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

    if device:
        # Remembered before the call: booting outlives the request that asked for it, so a capture must
        # be able to name the device even when starting it appeared to fail.
        _remember_device(key, device)
    else:
        console.print("Choosing a simulator that is quick to start...")
    # The flag is left out entirely rather than sent as 0: this is posted as form data, where every
    # value becomes text, and a "0" on the other side reads as true.
    payload = {"device": device} if device else ({"ipad": 1} if ipad else {})
    started = api.post(f"/builds/{key}/simulator/", json_data=payload)
    if not started:
        return
    device = started.get("device", device)
    _remember_device(key, device)
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
@click.option('--device', help="Simulator to photograph. Defaults to the one 'start' was given.")
def capture(key, device):
    """ Photographs what the simulator is showing, for the build with key \"KEY\".

    \f
    Run this once per screen you want on your App Store page: navigate to a screen, capture, navigate to
    the next, capture again. Apple takes up to ten per device size and needs at least one.

    The device is named rather than left to chance. A build machine usually has more than one simulator
    running — Xcode opens one of its own — and asking for "the booted one" then picks whichever it
    happens to find, which can quietly photograph the wrong phone.

    The image is kept with your app, ready to be sent to the App Store.
    """
    from odevio import api
    from odevio.settings import console

    if key is None:
        from odevio.helpers import terminal_menu
        key = terminal_menu("/builds/", "Build", does_not_exist_msg="You have no build running.")
        if key is None:
            return
    device = device or _remembered_device(key)
    if device is None:
        console.print("[warning]No simulator was started from here, so there is no way to tell which one "
                      "to photograph.[/warning]")
        console.print("Start one with [code]odevio screenshot start[/code], or name it with "
                      "[code]--device[/code].")
        return
    taken = api.post(f"/builds/{key}/screenshot/", json_data={"device": device})
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


# Apple's slots, largest first. These are the only sizes App Store Connect accepts, to the pixel, so
# they are also the sizes anything composed here has to be drawn at.
STORE_SIZES = {
    "6.9": (1320, 2868),
    "6.7": (1290, 2796),
    "6.5": (1242, 2688),
    "ipad": (2048, 2732),
}

def _app_base(key):
    """ API base of an app's screenshots, asking which app when no key is given. """
    from odevio.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return None
    return f"/applications/{key}"


def _listing_base(key):
    """ API base of a store listing's screenshots, asking which listing when no key is given. """
    from odevio.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/store-listings/", "Store listing",
                            does_not_exist_msg="You do not have any store listings. "
                                               "Create one with 'odevio screenshot listing create'.")
        if key is None:
            return None
    return f"/store-listings/{key}"


@screenshot.command()
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--file', 'files', multiple=True, required=True, type=click.Path(exists=True, dir_okay=False),
              help="An image to add: a raw capture or a finished picture. Repeat for several.")
@click.option('--size', type=click.Choice(list(STORE_SIZES)),
              help="Which slot it belongs to. Read from the image itself when it matches one exactly.")
@click.option('--replace', 'replace_id', type=int,
              help="Put the image in place of screenshot REPLACE (one --file): same slot, order and marketing visual.")
def upload(key, files, size, replace_id):
    """ Adds images to the App Store screenshots of the app with key \"KEY\".

    \f
    Raw captures from a phone or a simulator, to compose marketing visuals on, or pictures already
    finished in a design tool. What is added here appears in the editor alongside the rest and is sent
    to Apple by :code:`odevio screenshot push`.

    An image already at one of Apple's exact sizes keeps its pixels untouched. Anything else is scaled
    to the slot it is put in, which is what lets a picture App Store Connect refuses go through.

    Usage:
    """
    base = _app_base(key)
    if base:
        _upload(base, files, size, replace_id, "odevio screenshot ls")


def _upload(base, files, size, replace_id=None, ls_command=None):
    from odevio import api
    from odevio.settings import console

    if replace_id is not None:
        if len(files) != 1 or size:
            raise click.UsageError("--replace takes one --file, and no --size: the image keeps the slot it replaces.")
        _replace(base, replace_id, files[0], ls_command)
        return

    by_pixels = {dimensions: name for name, dimensions in STORE_SIZES.items()}

    for path in files:
        try:
            from PIL import Image
            with Image.open(path) as image:
                pixels = image.size
        except Exception as error:
            console.print(f"[warning]{path} could not be read:[/warning] {error}")
            continue

        slot = size or by_pixels.get(pixels)
        if slot is None:
            console.print(f"[warning]{path} is {pixels[0]} × {pixels[1]}, which is not one of Apple's "
                          "sizes.[/warning] Say which slot it is for with --size.")
            continue

        width, height = STORE_SIZES[slot]
        with open(path, "rb") as handle:
            created = api.post(
                f"{base}/screenshots/",
                json_data={"device_name": slot, "device_width": width, "device_height": height},
                files={"screenshot": handle},
            )
        if created:
            kept = "kept as it is" if pixels == (width, height) else f"scaled from {pixels[0]} × {pixels[1]}"
            console.print(f"[success]Added {path}[/success] as #{created['pk']} to the {slot} slot — {kept}.")


def _replace(base, screenshot_id, path, ls_command):
    from odevio import api
    from odevio.settings import console

    entry = _screenshot_entry(base, screenshot_id)
    if entry is None:
        console.print(f"[warning]No screenshot #{screenshot_id} here.[/warning] Run '{ls_command}' to see the ids.")
        return
    try:
        from PIL import Image
        with Image.open(path) as image:
            pixels = image.size
    except Exception as error:
        console.print(f"[warning]{path} could not be read:[/warning] {error}")
        return
    with open(path, "rb") as handle:
        replaced = api.patch(f"/screenshots/{screenshot_id}/", files={"screenshot": handle})
    if not replaced:
        return
    slot = (entry["width"], entry["height"])
    kept = "kept as it is" if pixels == slot else f"scaled from {pixels[0]} × {pixels[1]}"
    console.print(f"[success]Replaced the image of #{screenshot_id}[/success] — {kept}.")
    top, bottom = replaced.get("crop_top") or 0, replaced.get("crop_bottom") or 0
    if top or bottom:
        console.print(f"Its crop still applies ({top:.0%} off the top, {bottom:.0%} off the bottom); "
                      "crop it again with --top 0 --bottom 0 to show the whole capture.")
    if entry.get("visual_id"):
        after = _screenshot_entry(base, screenshot_id) or {}
        if after.get("visual_approved"):
            # A server older than this command keeps the approval, with a render of the old image.
            console.print("[warning]Its marketing visual still shows the old image.[/warning] "
                          "Preview it, then approve it again.")
        else:
            console.print("Its marketing visual now shows the new image: preview it, then approve it again.")


def _remove(base, screenshot_ids, ls_command):
    from odevio import api
    from odevio.settings import console

    entries = {row.get("id"): row for row in api.get(f"{base}/screenshot-list/") or []}
    for screenshot_id in screenshot_ids:
        entry = entries.get(screenshot_id)
        if entry is None:
            console.print(f"[warning]No screenshot #{screenshot_id} here.[/warning] Run '{ls_command}' to see the ids.")
            continue
        if api.delete(f"/screenshots/{screenshot_id}/", json_decode=False) is not False:
            console.print(f"[success]Deleted #{screenshot_id}[/success]"
                          + (", with its marketing visual." if entry.get("visual_id") else "."))


@screenshot.command("rm")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_ids', type=int, nargs=-1, required=True)
def rm(key, screenshot_ids):
    """ Deletes screenshots SCREENSHOT_IDS of the app "KEY", with the marketing visual composed on each.

    \f
    To change the image under a card and keep the card, use :code:`upload --replace` instead.

    Usage:
    """
    _remove(_app_base(key), screenshot_ids, "odevio screenshot ls")


def _font_cache_dir():
    import os

    from odevio.settings import get_config_path
    d = os.path.join(os.path.dirname(get_config_path()), "fonts")
    os.makedirs(d, exist_ok=True)
    return d


def _resolve_font(spec):
    """ Turn a "Family:400,700" spec into the structured font the renderer embeds.

    Fonts are pulled from fontsource (jsdelivr) rather than Google's gstatic: the gstatic woff2 does not
    decode in the render container's Chromium, while the fontsource files do. Each weight is cached on
    this machine so a font is fetched once, then reused offline.
    """
    import base64
    import os
    import urllib.request

    family, _, weights_str = spec.partition(":")
    family = family.strip()
    if not family:
        raise click.ClickException("Font must be given as 'Family' or 'Family:400,700'.")
    weights = [w.strip() for w in weights_str.split(",") if w.strip()] or ["400"]
    slug = family.lower().replace(" ", "-")
    faces = []
    for weight in weights:
        cache_path = os.path.join(_font_cache_dir(), f"{slug}-{weight}.woff2")
        if not os.path.exists(cache_path):
            url = (f"https://cdn.jsdelivr.net/npm/@fontsource/{slug}@5/files/"
                   f"{slug}-latin-{weight}-normal.woff2")
            try:
                with urllib.request.urlopen(url, timeout=20) as resp:
                    data = resp.read()
            except Exception as error:
                raise click.ClickException(
                    f"Could not fetch {family} {weight} from fontsource ({error}). "
                    f"Check the family name and that the weight exists.")
            with open(cache_path, "wb") as fh:
                fh.write(data)
        with open(cache_path, "rb") as fh:
            faces.append({"weight": int(weight), "woff2_b64": base64.b64encode(fh.read()).decode()})
    return {"family": family, "faces": faces}


def _screenshot_entry(base, screenshot_id):
    """ Look up one screenshot in an app's or listing's list, returning its entry or None. """
    from odevio import api
    rows = api.get(f"{base}/screenshot-list/") or []
    for row in rows:
        if row.get("id") == screenshot_id:
            return row
    return None


@screenshot.command("ls")
@login_required_warning_decorator
@click.argument('key', required=False)
def ls(key):
    """ Lists the raw screenshots of the app with key \"KEY\", with their id, size and visual state.

    \f
    The id is how a marketing visual is targeted: :code:`odevio screenshot visual KEY <id>`.

    Usage:
    """
    base = _app_base(key)
    if base:
        _ls(base)


def _ls(base):
    from rich.table import Table

    from odevio import api
    from odevio.settings import console

    rows = api.get(f"{base}/screenshot-list/")
    if not rows:
        console.print("No screenshots yet. Upload some in the editor first.")
        return
    table = Table("id", "file", "size", "marketing visual")
    for row in rows:
        if row.get("has_visual"):
            state = "approved" if row.get("visual_approved") else "draft"
        else:
            state = "—"
        table.add_row(f"#{row['id']}", row.get("file") or "", f"{row['width']}×{row['height']}", state)
    console.print(table)


@screenshot.command("crop")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.argument('screenshot_id', type=int)
@click.option('--top', type=float, default=0.0, show_default=True, help="Share of the height cut at the top, 0.1 = 10%.")
@click.option('--bottom', type=float, default=0.0, show_default=True, help="Share of the height cut at the bottom.")
def crop(key, screenshot_id, top, bottom):
    """ Crops screenshot SCREENSHOT_ID of the app \"KEY\" (KEY required): cuts the top and bottom, zooming in.

    \f
    The sides are cut by as much, so the shot keeps its proportions; :code:`--top 0 --bottom 0` restores
    the whole capture. A marketing visual is composed over the cropped shot, so it has to be previewed
    and approved again.

    Usage:
    """
    base = _app_base(key)
    if base:
        _crop(base, screenshot_id, top, bottom, "odevio screenshot ls")


def _crop(base, screenshot_id, top, bottom, ls_command):
    from odevio import api
    from odevio.settings import console

    if not (0 <= top and 0 <= bottom and top + bottom < 0.8):
        raise click.UsageError("--top and --bottom are shares of the height, together under 0.8.")
    entry = _screenshot_entry(base, screenshot_id)
    if entry is None:
        console.print(f"[warning]No screenshot #{screenshot_id} here.[/warning] Run '{ls_command}' to see the ids.")
        return
    side = (top + bottom) / 2
    if api.patch(f"/screenshots/{screenshot_id}/", json_body={
            "crop_top": top, "crop_bottom": bottom, "crop_left": side, "crop_right": side}):
        console.print(f"[success]Cropped #{screenshot_id}[/success]: {top:.0%} off the top, {bottom:.0%} off the bottom.")
        if entry.get("visual_id"):
            console.print("Its marketing visual is no longer approved: preview it, then approve it again.")


@screenshot.command("visuals")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--json', 'as_json', is_flag=True, help="Print the full props, to reuse them for the next card.")
def visuals(key, as_json):
    """ Shows the marketing visuals of the app with key \"KEY\": template, headline, colours and font.

    \f
    Read this before composing another card, so the set stays one campaign: reuse the background, font
    and template of the cards already there.

    Usage:
    """
    base = _app_base(key)
    if base:
        _visuals(base, as_json)


def _visuals(base, as_json):
    import json

    from rich.table import Table

    from odevio import api
    from odevio.settings import console

    rows = []
    for entry in api.get(f"{base}/screenshot-list/") or []:
        if not entry.get("visual_id"):
            continue
        visual = api.get(f"/marketing-visuals/{entry['visual_id']}/")
        if not visual:
            continue
        rows.append({
            "screenshot_id": entry["id"],
            "positions": entry.get("positions"),
            "approved": bool(visual.get("approved")),
            "template": visual.get("template") or "custom",
            "series": visual.get("series"),
            "needs_approval": bool(visual.get("needs_approval")),
            "font": (visual.get("font") or {}).get("family"),
            "last_edited_by": visual.get("last_edited_by", "agent"),
            "props": visual.get("props") or {},
        })
    if as_json:
        click.echo(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        console.print("No marketing visuals yet.")
        return
    table = Table("id", "position", "state", "template", "headline", "background", "font", "last edited by")
    for row in rows:
        props = row["props"]
        step = row["series"]
        layout = f"{step['template']} · step {step['step']}" if step else row["template"]
        state = "needs approval" if row["needs_approval"] else "approved" if row["approved"] else "draft"
        table.add_row(f"#{row['screenshot_id']}", _positions(row["positions"]), state, layout,
                      str(props.get("headline", "")), str(props.get("background", "series" if step else "")),
                      row["font"] or ("series" if step else "—"),
                      row["last_edited_by"])
    console.print(table)


@screenshot.command("templates")
@login_required_warning_decorator
@click.argument('name', required=False)
@click.option('--json', 'as_json', is_flag=True, help="Print the list as JSON (without NAME).")
@click.option('--presets', is_flag=True, help="List the shipped series presets instead.")
def templates(name, as_json, presets):
    """ Lists the shipped marketing-visual templates, or prints the JSX of template NAME.

    \f
    The JSX's comments explain each prop the template reads; start a template of your own from it.

    Usage:
    """
    import json

    from rich.table import Table

    from odevio import api
    from odevio.settings import console

    if name:
        try:
            template = api.get(f"/marketing-templates/{name}/")
        except api.NotFoundException:
            raise click.ClickException(f"No template named '{name}'. Run 'odevio screenshot templates' to list them.")
        if template:
            click.echo(template["jsx_source"])
        return
    if presets:
        rows = api.get("/marketing-templates/presets/") or []
        if as_json:
            click.echo(json.dumps(rows, indent=2, ensure_ascii=False))
            return
        table = Table("preset", "layouts", "what it looks like")
        for row in rows:
            table.add_row(row["name"], " · ".join(row["templates"]), row.get("description", ""))
        console.print(table)
        console.print("Steps alternate the main and the alternate palette when the theme has both.")
        return
    rows = api.get("/marketing-templates/")
    if rows is None:
        return
    if as_json:
        click.echo(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    table = Table("name", "span", "description", "props")
    for row in rows:
        table.add_row(row["name"], str(row.get("span") or 1), row["description"], ", ".join(row["props"]))
    console.print(table)


@screenshot.command("visual")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.argument('screenshot_id', type=int)
@click.option('--template', help="A shipped layout by name (see 'odevio screenshot templates'). Or give your own with --jsx-file.")
@click.option('--jsx-file', type=click.Path(exists=True, dir_okay=False),
              help="Your own React component (default export) for the visual.")
@click.option('--props-file', type=click.Path(exists=True, dir_okay=False),
              help="JSON props for the component.")
@click.option('--font', 'font_spec', help="Google Font to embed, e.g. 'Inter:600,800'.")
@click.option('--force', is_flag=True, help="Overwrite a visual the user retouched in the editor.")
@click.option('--follow-series', is_flag=True,
              help="Give the card its series' layout again, after it kept a template of its own.")
def visual(key, screenshot_id, template, jsx_file, props_file, font_spec, force, follow_series):
    """ Creates or updates the marketing visual for screenshot SCREENSHOT_ID of the app \"KEY\".

    \f
    One visual per screenshot: running this again on the same id updates it in place and resets its
    approval, so it never ships a stale image. The result is visible in the editor after a refresh.
    A visual the user retouched in the editor is refused unless :code:`--force`.

    Usage:
    """
    base = _app_base(key)
    if base:
        _visual(base, screenshot_id, template, jsx_file, props_file, font_spec, "odevio screenshot ls", force,
                follow_series)


def _visual(base, screenshot_id, template, jsx_file, props_file, font_spec, ls_command, force=False,
            follow_series=False):
    import json

    from odevio import api
    from odevio.settings import console

    if template and jsx_file:
        raise click.UsageError("Give either --template or --jsx-file, not both.")

    entry = _screenshot_entry(base, screenshot_id)
    if entry is None:
        console.print(f"[warning]No screenshot #{screenshot_id} here.[/warning] "
                      f"Run '{ls_command}' to see the ids.")
        return

    props = {}
    if props_file:
        with open(props_file) as fh:
            props = json.load(fh)
    payload = {"source_screenshot": screenshot_id, "props": props}
    if template:
        payload["template"] = template
    elif jsx_file:
        with open(jsx_file) as fh:
            payload["jsx_source"] = fh.read()
    if follow_series:
        payload["follows_sequence"] = True
    if font_spec:
        payload["font"] = _resolve_font(font_spec)
    if force:
        payload["force"] = True

    if entry.get("visual_id"):
        result = api.put(f"/marketing-visuals/{entry['visual_id']}/", json_body=payload)
        action = "Updated"
    else:
        result = api.post("/marketing-visuals/", json_body=payload)
        action = "Created"
    if not result:
        return
    visual_id = result.get("pk")

    # Dry-run compile through the preview route so a broken component is caught now, not at approve.
    api.get(f"/marketing-visuals/{visual_id}/preview/", json_decode=False)
    console.print(f"[success]{action} the marketing visual for #{screenshot_id}.[/success] "
                  "Refresh the editor to see it.")


@screenshot.command("approve-visual")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.argument('screenshot_ids', type=int, nargs=-1)
@click.option('--all', 'approve_changed', is_flag=True,
              help="Approve again every card a change of the series un-approved (KEY required).")
@click.option('--except', 'except_ids', multiple=True,
              help="With --all: leave these screenshot ids out, e.g. --except 12,14.")
@click.option('--out-dir', type=click.Path(file_okay=False), help="Also save each approved PNG in this folder.")
@click.pass_context
def approve_visual(ctx, key, screenshot_ids, approve_changed, except_ids, out_dir):
    """ Renders and approves the marketing visuals of screenshots SCREENSHOT_IDS of the app \"KEY\" (KEY required).

    \f
    Approving renders the submission PNG and marks the visual as the image that replaces the raw
    screenshot on the App Store. Nothing is sent to Apple until :code:`odevio screenshot push`.

    Usage:
    """
    if approve_changed:
        if not key or screenshot_ids:
            raise click.UsageError("Give the app key and --all, without screenshot ids.")
        ctx.invoke(listing_approve_visual, key=_listing_of_app(key), screenshot_ids=(), approve_changed=True,
                   except_ids=except_ids, out_dir=out_dir)
        return
    if except_ids:
        raise click.UsageError("--except only goes with --all.")
    if not screenshot_ids:
        raise click.UsageError("Give screenshot ids, or --all.")
    base = _app_base(key)
    if base:
        _render_visuals(base, screenshot_ids, True, out_dir, "odevio screenshot visual")


@screenshot.command("preview")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.argument('screenshot_ids', type=int, nargs=-1, required=True)
@click.option('--out-dir', type=click.Path(file_okay=False), default=".", show_default=True,
              help="Folder the preview PNGs are saved in.")
def preview(key, screenshot_ids, out_dir):
    """ Renders the marketing visuals of SCREENSHOT_IDS of the app \"KEY\" (KEY required) as drafts, saving the PNGs.

    \f
    The exact image approval would produce, without approving it: look at it before asking the user.

    Usage:
    """
    base = _app_base(key)
    if base:
        _render_visuals(base, screenshot_ids, False, out_dir, "odevio screenshot visual")


def _wait_for_render(visual_id, task_id):
    """ Poll a render task until it settles; None if it never does. """
    import time

    from odevio import api

    # Past the server's worst case: compile, a capture that hangs and is killed, its retry, and a queue.
    for _ in range(200):
        time.sleep(1.5)
        status = api.get(f"/marketing-visuals/{visual_id}/approve-status/{task_id}/") or {}
        if status.get("state") in ("SUCCESS", "FAILURE"):
            return status
    return None


def _save_png(visual_id, out_dir, name):
    """ Download a visual's last render into OUT_DIR, returning the files written: the render, then, for a
    card spanning several App Store positions, one image per position (NAME-1.png, NAME-2.png). """
    import os
    from urllib.parse import urlparse

    from odevio import api
    from odevio.settings import API_BASE_URL

    visual = api.get(f"/marketing-visuals/{visual_id}/") or {}
    url = visual.get("rendered_png")
    if not url:
        return []
    # The server may name itself by an internal host; the file is always reached through the API's own.
    parts = urlparse(url)
    downloads = [(name, API_BASE_URL + parts.path + (f"?{parts.query}" if parts.query else ""))]
    stem = os.path.splitext(name)[0]
    span = visual.get("span") or 1
    if span > 1:
        downloads += [(f"{stem}-{position}.png",
                       f"{API_BASE_URL}/api/v1/marketing-visuals/{visual_id}/slot-image/{position}/")
                      for position in range(1, span + 1)]
    paths = []
    for file_name, file_url in downloads:
        content = _download(file_url, file_name)
        if content is None:
            continue
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, file_name)
        with open(path, "wb") as handle:
            handle.write(content)
        paths.append(path)
    return paths


def _download(url, file_name):
    """ The bytes at URL, fetched with the user's authorization; None after printing why not. """
    import requests

    from odevio import api
    from odevio.settings import console

    try:
        response = requests.get(url, headers={"Authorization": api.get_authorization_header()}, timeout=60)
    except requests.RequestException as error:
        console.print(f"[warning]Could not download {file_name}:[/warning] {error}")
        return None
    if not response.ok:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = None
        console.print(f"[warning]Could not download {file_name}:[/warning] {detail or f'HTTP {response.status_code}'}")
        return None
    if not response.content:
        console.print(f"[warning]Could not download {file_name}:[/warning] the server sent an empty file. "
                      "Look at the card in the editor instead.")
        return None
    return response.content


def _render_visuals(base, screenshot_ids, approve, out_dir, visual_command, linked=True):
    """ Render the visuals of these screenshots, as drafts or approved, saving the PNGs when asked. """
    from odevio import api
    from odevio.settings import console

    entries = {row.get("id"): row for row in api.get(f"{base}/screenshot-list/") or []}
    for screenshot_id in screenshot_ids:
        entry = entries.get(screenshot_id)
        if entry is None or not entry.get("visual_id"):
            console.print(f"[warning]No marketing visual on #{screenshot_id}.[/warning] "
                          f"Create one with '{visual_command}' first.")
            continue
        visual_id = entry["visual_id"]
        started = api.post(f"/marketing-visuals/{visual_id}/{'approve' if approve else 'render'}/", json_data={})
        if not started:
            continue
        console.print(f"Rendering #{screenshot_id}…")
        status = _wait_for_render(visual_id, started.get("task_id"))
        if status is None:
            console.print(f"[warning]#{screenshot_id}: render timed out.[/warning] Try again.")
            continue
        if status["state"] == "FAILURE":
            console.print(f"[warning]#{screenshot_id}: render failed:[/warning] {status.get('error', 'unknown error')}")
            continue
        if approve:
            console.print(f"[success]Approved the marketing visual for #{screenshot_id}.[/success] "
                          + ("It will replace the raw screenshot on the next push." if linked
                             else "Nothing goes to Apple: the listing is not linked to an app."))
        else:
            console.print(f"[success]Rendered a draft of #{screenshot_id}.[/success] Not approved: nothing ships yet.")
        if out_dir:
            for path in _save_png(visual_id, out_dir, f"{'approved' if approve else 'preview'}-{screenshot_id}.png"):
                console.print(f"Saved to {path}")


def _positions(positions):
    """ App Store positions as the store numbers them: '2', or '2-3' for a card spanning two. """
    if not positions:
        return "—"
    return str(positions[0]) if len(positions) == 1 else f"{positions[0]}-{positions[-1]}"


def _listing_of_app(app_key):
    """ The key of the store listing an app's screenshots live in. """
    from odevio import api

    for row in api.get("/store-listings/") or []:
        if row.get("application") == app_key:
            return row["key"]
    raise click.ClickException(
        f"The app {app_key} has no screenshots yet, so no listing to give a series. Upload or capture some first.")


@screenshot.command("series")
@login_required_warning_decorator
@click.argument('key')
@click.option('--json', 'as_json', is_flag=True, help="Print the series and each card's step as JSON.")
@click.option('--from-card', 'from_card', type=int,
              help="Turn the series on from the card of screenshot ID: its look becomes the theme, nothing re-renders.")
@click.option('--dry-run', is_flag=True, help="With --from-card: show the series it would create, change nothing.")
@click.option('--theme-file', type=click.Path(exists=True, dir_okay=False),
              help="JSON theme: palette, alternate_palette, eyebrow, font (a font of the listing by name) and motif.")
@click.option('--font', 'font_spec', help="Google Font for every card, e.g. 'Fraunces:600,800'.")
@click.option('--sequence', help="Steps as template[:main|alternate], comma-separated, e.g. 'statement,tilt:alternate,lens'.")
@click.option('--preset', help="A shipped sequence by name (see 'odevio screenshot templates --presets').")
@click.option('--motif', help="A backdrop drawn across all the cards: waves, discs, diagonal, glow, grid, chevrons, "
                              "ribbon, sparkles, or none.")
@click.option('--off', is_flag=True, help="Turn the series off; each card keeps what it shows, but its motif.")
@click.pass_context
def series(ctx, key, **options):
    """ Shows or sets the series of the app with key \"KEY\": one theme and one sequence of layouts for its cards. """
    ctx.invoke(listing_series, key=_listing_of_app(key), **options)


@screenshot.group()
def listing():
    """ Store listings: an app's screenshots and marketing visuals, with or without an Apple account.

    \f
    A store listing holds what the App Store shows — the screenshots and the marketing visuals composed
    over them. It needs no Apple developer account and no build, so it can be prepared before the app is
    built on Odevio, then attached with :code:`odevio screenshot listing link`. An app you already build
    on Odevio gets its listing on its own: use the plain screenshot commands with the app key.

    App keys and listing keys are separate: a listing is always addressed through these commands.

    Usage:
    """


@listing.command("create")
@login_required_warning_decorator
@click.argument('name')
@click.option('--team', 'team_key', help="Share the listing with this team right away.")
def listing_create(name, team_key):
    """ Creates a store listing named \"NAME\" and prints its key. """
    from odevio import api
    from odevio.settings import console

    created = api.post("/store-listings/", json_body={"name": name})
    if not created:
        return
    key = created["key"]
    if team_key:
        api.post(f"/store-listings/{key}/teams/{team_key}/", json_body={})
    console.print(f"[success]Created the store listing {key}[/success] ('{name}'). "
                  f"Add images with 'odevio screenshot listing upload {key} --file <image>'.")


@listing.command("ls")
@login_required_warning_decorator
def listing_ls():
    """ Lists the store listings you can reach, with their key and linked app. """
    from rich.table import Table

    from odevio import api
    from odevio.settings import console

    rows = api.get("/store-listings/")
    if not rows:
        console.print("No store listings yet. Create one with 'odevio screenshot listing create'.")
        return
    table = Table("key", "name", "app", "owner")
    for row in rows:
        table.add_row(row["key"], row["name"], row.get("application") or "—", row.get("owner") or "")
    console.print(table)


@listing.command("screenshots")
@login_required_warning_decorator
@click.argument('key', required=False)
def listing_screenshots(key):
    """ Lists the raw screenshots of the store listing \"KEY\", with their id, size and visual state. """
    base = _listing_base(key)
    if base:
        _ls(base)


@listing.command("series")
@login_required_warning_decorator
@click.argument('key')
@click.option('--json', 'as_json', is_flag=True, help="Print the series and each card's step as JSON.")
@click.option('--from-card', 'from_card', type=int,
              help="Turn the series on from the card of screenshot ID: its look becomes the theme, nothing re-renders.")
@click.option('--dry-run', is_flag=True, help="With --from-card: show the series it would create, change nothing.")
@click.option('--theme-file', type=click.Path(exists=True, dir_okay=False),
              help="JSON theme: palette, alternate_palette, eyebrow, font (a font of the listing by name) and motif.")
@click.option('--font', 'font_spec', help="Google Font for every card, e.g. 'Fraunces:600,800'.")
@click.option('--sequence', help="Steps as template[:main|alternate], comma-separated, e.g. 'statement,tilt:alternate,lens'.")
@click.option('--preset', help="A shipped sequence by name (see 'odevio screenshot templates --presets').")
@click.option('--motif', help="A backdrop drawn across all the cards: waves, discs, diagonal, glow, grid, chevrons, "
                              "ribbon, sparkles, or none.")
@click.option('--off', is_flag=True, help="Turn the series off; each card keeps what it shows, but its motif.")
def listing_series(key, as_json, from_card, dry_run, theme_file, font_spec, sequence, preset, motif, off):
    """ Shows or sets the series of the store listing \"KEY\": one theme and one sequence of layouts for its cards.

    \f
    A card on a series brings only its words; its colours, eyebrow, font and layout come from the series,
    by its position, unless the card keeps one as an exception. Changing the series un-approves exactly
    the cards whose image changes; 'approve-visual KEY --all' approves them again.

    Usage:
    """
    import json

    from odevio import api
    from odevio.settings import console

    base = f"/store-listings/{key}/series/"
    if off:
        losing = 0
        if _current_theme(base).get("motif"):
            losing = sum(1 for card in _series_cards(key) if card["approved"] and card["motif"])
        try:
            deleted = api.delete(base, json_decode=False)
        except api.NotFoundException:
            raise click.ClickException("This listing has no series.")
        if deleted is not False:
            console.print("[success]The series is off.[/success] Each card keeps what it showed"
                          + (f", but {losing} card{'s' if losing > 1 else ''} lost the motif and "
                             f"need{'' if losing > 1 else 's'} approval: "
                             f"'odevio screenshot listing approve-visual {key} --all'." if losing else "."))
        return
    if from_card is not None:
        route = f"{base}from-card/{from_card}/"
        try:
            derived = api.get(route) if dry_run else api.post(route, json_data={})
        except api.NotFoundException:
            raise click.ClickException(f"No marketing visual on screenshot #{from_card} of this listing.")
        if not derived:
            return
        if dry_run:
            console.print(f"Would create this series; {derived.get('exceptions', 0)} value(s) would stay the cards' own.")
            _print_series(_compact(derived), [], as_json)
            return
        console.print("[success]Series created.[/success] Nothing re-renders: every card keeps its look.")
    elif theme_file or font_spec or sequence or preset or motif:
        body = {}
        if theme_file or font_spec or motif:
            with open(theme_file) if theme_file else _nullcontext() as fh:
                theme = json.load(fh) if fh else _current_theme(base)
            if font_spec:
                theme["font"] = _resolve_font(font_spec)
            if motif:
                theme["motif"] = "none" if motif == "none" else {"shape": motif}
            body["theme"] = theme
        if sequence:
            body["sequence"] = _parse_sequence(sequence)
        if preset:
            body["preset"] = preset
        if not api.put(base, json_body=body):
            return
    try:
        series = api.get(base)
    except api.NotFoundException:
        console.print("This listing has no series. Turn one on with --from-card ID, "
                      "or set it with --theme-file and --sequence (or --preset).")
        return
    _print_series(_compact(series), _series_cards(key), as_json)


def _nullcontext():
    import contextlib

    return contextlib.nullcontext()


def _current_theme(base):
    from odevio import api

    try:
        return _compact(api.get(base) or {}).get("theme") or {}
    except api.NotFoundException:
        return {}


def _compact(series):
    """ The series with its fonts named, not embedded: what a person reads and a theme file holds. """
    theme = dict(series.get("theme") or {})
    if isinstance(theme.get("font"), dict):
        theme["font"] = theme["font"]["family"]
    if theme.get("fonts"):
        theme["fonts"] = [f["family"] if isinstance(f, dict) else f for f in theme["fonts"]]
    return {**series, "theme": theme}


def _parse_sequence(text):
    steps = []
    for part in [p.strip() for p in text.split(",") if p.strip()]:
        template, _, palette = part.partition(":")
        palette = palette or "main"
        if palette in ("alt", "alternate"):
            palette = "alternate"
        steps.append({"template": template.strip(), "palette": palette})
    return steps


def _series_cards(key):
    """ Each card of the listing with its step, its effective layout and its exceptions. """
    from odevio import api

    cards = []
    for entry in api.get(f"/store-listings/{key}/screenshot-list/") or []:
        if not entry.get("visual_id"):
            continue
        visual = api.get(f"/marketing-visuals/{entry['visual_id']}/") or {}
        state = visual.get("series") or {}
        cards.append({"screenshot_id": entry["id"], "positions": entry.get("positions"),
                      "step": state.get("step"), "template": state.get("template"),
                      "palette": state.get("palette"), "exceptions": state.get("exceptions") or [],
                      "approved": bool(visual.get("approved")), "needs_approval": bool(visual.get("needs_approval")),
                      # Servers before the field: every card not turning it off drew it.
                      "motif": visual.get("motif", "motif" not in (state.get("exceptions") or []))})
    return cards


def _print_series(series, cards, as_json):
    import json

    from rich.table import Table

    from odevio.settings import console

    if as_json:
        click.echo(json.dumps({"series": series, "cards": cards}, indent=2, ensure_ascii=False))
        return
    theme = series.get("theme") or {}
    console.print(f"Font: {theme.get('font') or 'Inter'} · Eyebrow: {theme.get('eyebrow') or '—'}")
    console.print(f"Main palette: {json.dumps(theme.get('palette') or {})}")
    if theme.get("alternate_palette"):
        console.print(f"Alternate palette: {json.dumps(theme['alternate_palette'])}")
    console.print(f"Motif: {(theme.get('motif') or {}).get('shape') or 'none'}")
    console.print("Sequence: " + " · ".join(
        f"{i + 1} {s['template']}{' (alt)' if s.get('palette') == 'alternate' else ''}"
        for i, s in enumerate(series.get("sequence") or [])))
    if not cards:
        return
    table = Table("id", "position", "step", "layout", "palette", "exceptions", "state")
    for card in cards:
        state = "needs approval" if card["needs_approval"] else "approved" if card["approved"] else "draft"
        table.add_row(f"#{card['screenshot_id']}", _positions(card["positions"]), str(card["step"] or "—"),
                      card["template"] or "—",
                      card["palette"] or "—", ", ".join(card["exceptions"]) or "—", state)
    console.print(table)


@listing.command("visuals")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--json', 'as_json', is_flag=True, help="Print the full props, to reuse them for the next card.")
def listing_visuals(key, as_json):
    """ Shows the marketing visuals of the store listing \"KEY\": template, headline, colours and font. """
    base = _listing_base(key)
    if base:
        _visuals(base, as_json)


@listing.command("upload")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--file', 'files', multiple=True, required=True, type=click.Path(exists=True, dir_okay=False),
              help="An image to add: a raw capture or a finished picture. Repeat for several.")
@click.option('--size', type=click.Choice(list(STORE_SIZES)),
              help="Which slot it belongs to. Read from the image itself when it matches one exactly.")
@click.option('--replace', 'replace_id', type=int,
              help="Put the image in place of screenshot REPLACE (one --file): same slot, order and marketing visual.")
def listing_upload(key, files, size, replace_id):
    """ Adds images to the store listing \"KEY\" — raw captures or finished pictures — at Apple's exact slot size. """
    base = _listing_base(key)
    if base:
        _upload(base, files, size, replace_id, f"odevio screenshot listing screenshots {base.rsplit('/', 1)[-1]}")


@listing.command("rm")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_ids', type=int, nargs=-1, required=True)
def listing_rm(key, screenshot_ids):
    """ Deletes screenshots SCREENSHOT_IDS of the listing \"KEY\", with the marketing visual composed on each. """
    _remove(f"/store-listings/{key}", screenshot_ids, f"odevio screenshot listing screenshots {key}")


@listing.command("visual")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_id', type=int)
@click.option('--template', help="A shipped layout by name (see 'odevio screenshot templates'). Or give your own with "
                                   "--jsx-file. On a listing with a series, leave both out: the card takes its step's layout.")
@click.option('--jsx-file', type=click.Path(exists=True, dir_okay=False),
              help="Your own React component (default export) for the visual.")
@click.option('--props-file', type=click.Path(exists=True, dir_okay=False),
              help="JSON props for the component.")
@click.option('--font', 'font_spec', help="Google Font to embed, e.g. 'Inter:600,800'.")
@click.option('--force', is_flag=True, help="Overwrite a visual the user retouched in the editor.")
@click.option('--follow-series', is_flag=True,
              help="Give the card its series' layout again, after it kept a template of its own.")
def listing_visual(key, screenshot_id, template, jsx_file, props_file, font_spec, force, follow_series):
    """ Creates or updates the marketing visual for screenshot SCREENSHOT_ID of the listing \"KEY\". """
    _visual(f"/store-listings/{key}", screenshot_id, template, jsx_file, props_file, font_spec,
            f"odevio screenshot listing screenshots {key}", force, follow_series)


@listing.command("approve-visual")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_ids', type=int, nargs=-1)
@click.option('--all', 'approve_changed', is_flag=True,
              help="Approve again every card a change of the series un-approved. Drafts never approved are left alone.")
@click.option('--except', 'except_ids', multiple=True,
              help="With --all: leave these screenshot ids out, e.g. --except 12,14.")
@click.option('--out-dir', type=click.Path(file_okay=False), help="Also save each approved PNG in this folder.")
def listing_approve_visual(key, screenshot_ids, approve_changed, except_ids, out_dir):
    """ Renders and approves the marketing visuals of screenshots SCREENSHOT_IDS of the listing \"KEY\". """
    from odevio import api
    from odevio.settings import console

    if except_ids and not approve_changed:
        raise click.UsageError("--except only goes with --all.")
    if bool(screenshot_ids) == approve_changed:
        raise click.UsageError("Give screenshot ids, or --all.")
    listing = api.get(f"/store-listings/{key}/")
    if not listing:
        return
    base = f"/store-listings/{key}"
    if except_ids:
        screenshot_ids = _needing_approval(base, _id_list(except_ids))
        if not screenshot_ids:
            console.print("No other card needs approval again.")
            return
    if screenshot_ids:
        _render_visuals(base, screenshot_ids, True, out_dir, "odevio screenshot listing visual",
                        bool(listing.get("application")))
        return
    started = api.post(f"/store-listings/{key}/approve-all/", json_data={})
    if not started:
        return
    tasks = started.get("tasks") or []
    if not tasks:
        console.print("No card needs approval again.")
        return
    console.print(f"Rendering {len(tasks)} card{'s' if len(tasks) > 1 else ''}…")
    for task in tasks:
        status = _wait_for_render(task["visual"], task["task_id"])
        if status is None:
            console.print(f"[warning]Visual {task['visual']}: render timed out.[/warning] Try again.")
        elif status["state"] == "FAILURE":
            console.print(f"[warning]Visual {task['visual']}: render failed:[/warning] {status.get('error', 'unknown error')}")
        elif out_dir:
            for path in _save_png(task["visual"], out_dir, f"approved-visual-{task['visual']}.png"):
                console.print(f"Saved to {path}")
    console.print("[success]Done.[/success] Run 'odevio screenshot listing visuals " + key + "' to check.")


def _id_list(values):
    """ Screenshot ids given as repeated options, comma-separated, or both. """
    try:
        return {int(part) for value in values for part in value.split(",") if part.strip()}
    except ValueError:
        raise click.UsageError("--except takes screenshot ids, e.g. --except 12,14.")


def _needing_approval(base, excluded):
    """ The screenshots whose card lost its approval, as the server's approve-all picks them, but EXCLUDED. """
    from odevio import api

    ids = []
    for entry in api.get(f"{base}/screenshot-list/") or []:
        if not entry.get("visual_id") or entry["id"] in excluded:
            continue
        visual = api.get(f"/marketing-visuals/{entry['visual_id']}/") or {}
        if visual.get("needs_approval"):
            ids.append(entry["id"])
    return ids


@listing.command("preview")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_ids', type=int, nargs=-1, required=True)
@click.option('--out-dir', type=click.Path(file_okay=False), default=".", show_default=True,
              help="Folder the preview PNGs are saved in.")
def listing_preview(key, screenshot_ids, out_dir):
    """ Renders the marketing visuals of SCREENSHOT_IDS of the listing \"KEY\" as drafts and saves the PNGs. """
    _render_visuals(f"/store-listings/{key}", screenshot_ids, False, out_dir, "odevio screenshot listing visual")


@listing.command("crop")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_id', type=int)
@click.option('--top', type=float, default=0.0, show_default=True, help="Share of the height cut at the top, 0.1 = 10%.")
@click.option('--bottom', type=float, default=0.0, show_default=True, help="Share of the height cut at the bottom.")
def listing_crop(key, screenshot_id, top, bottom):
    """ Crops screenshot SCREENSHOT_ID of the listing \"KEY\": cuts the top and bottom, zooming in. """
    _crop(f"/store-listings/{key}", screenshot_id, top, bottom, f"odevio screenshot listing screenshots {key}")


@listing.command("share")
@login_required_warning_decorator
@click.argument('key')
@click.argument('team_key')
def listing_share(key, team_key):
    """ Shares the store listing \"KEY\" with the team \"TEAM_KEY\", so its members can work on it. """
    from odevio import api
    from odevio.settings import console

    if api.post(f"/store-listings/{key}/teams/{team_key}/", json_body={}):
        console.print(f"[success]Shared {key} with the team {team_key}.[/success]")


@listing.command("unshare")
@login_required_warning_decorator
@click.argument('key')
@click.argument('team_key')
def listing_unshare(key, team_key):
    """ Stops sharing the store listing \"KEY\" with the team \"TEAM_KEY\". """
    from odevio import api
    from odevio.settings import console

    if api.delete(f"/store-listings/{key}/teams/{team_key}/"):
        console.print(f"[success]{key} is no longer shared with the team {team_key}.[/success]")


@listing.command("link")
@login_required_warning_decorator
@click.argument('key')
@click.argument('app_key')
def listing_link(key, app_key):
    """ Attaches the store listing \"KEY\" to the app \"APP_KEY\", once you build it on Odevio. """
    from odevio import api
    from odevio.settings import console

    try:
        linked = api.post(f"/store-listings/{key}/link/{app_key}/", json_body={})
    except api.NotFoundException:
        console.print("One of these keys is invalid or you do not have access to it.")
        return
    if linked:
        console.print(f"[success]{key} is now the store listing of {app_key}.[/success] Its screenshots "
                      f"stay as they are; 'odevio screenshot push {app_key}' sends them to Apple.")


@listing.command("unlink")
@login_required_warning_decorator
@click.argument('key')
def listing_unlink(key):
    """ Detaches the store listing \"KEY\" from its app; its screenshots and visuals stay in the listing. """
    from odevio import api
    from odevio.settings import console

    try:
        unlinked = api.post(f"/store-listings/{key}/unlink/", json_body={})
    except api.NotFoundException:
        console.print("This key is invalid or you do not have access to it.")
        return
    if unlinked:
        console.print(f"[success]{key} is no longer attached to an app.[/success] Link it to the right one with "
                      f"'odevio screenshot listing link {key} <app-key>'.")


@listing.command("open")
@login_required_warning_decorator
@click.argument('key', required=False)
def listing_open(key):
    """ Returns a link to the screenshot editor for the store listing \"KEY\". """
    from odevio import api
    from odevio.settings import API_BASE_URL, console

    base = _listing_base(key)
    if not base:
        return
    try:
        link = api.get(f"{base}/editor/")
    except api.NotFoundException:
        console.print("This key is invalid or you do not have access to it.")
        return
    if link:
        console.print("Here's the link to the screenshot editor:")
        console.print(f"[link]{API_BASE_URL}{link['url']}[/link]")
