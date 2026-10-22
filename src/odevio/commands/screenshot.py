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

# The layouts shipped with the skill, by the name an agent or a user asks for.
TEMPLATES = {
    "classic": "appstore_card.jsx",
    "editorial": "appstore_card_editorial.jsx",
    "hero": "appstore_card_hero.jsx",
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
def upload(key, files, size):
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
        _upload(base, files, size)


def _upload(base, files, size):
    from odevio import api
    from odevio.settings import console

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
            console.print(f"[success]Added {path}[/success] to the {slot} slot — {kept}.")


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


def _template_name(jsx_source):
    """ Which shipped template a visual was built from, or "custom" when it was written by hand. """
    import os

    from odevio.commands.skill import skill_source

    folder = os.path.join(skill_source(), "references", "templates")
    for name in sorted(os.listdir(folder)):
        with open(os.path.join(folder, name)) as fh:
            if fh.read().strip() == (jsx_source or "").strip():
                return name
    return "custom"


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
            "approved": bool(visual.get("approved")),
            "template": _template_name(visual.get("jsx_source")),
            "font": (visual.get("font") or {}).get("family"),
            "props": visual.get("props") or {},
        })
    if as_json:
        click.echo(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        console.print("No marketing visuals yet.")
        return
    table = Table("id", "state", "template", "headline", "background", "font")
    for row in rows:
        props = row["props"]
        table.add_row(f"#{row['screenshot_id']}", "approved" if row["approved"] else "draft", row["template"],
                      str(props.get("headline", "")), str(props.get("background", "")), row["font"] or "—")
    console.print(table)


@screenshot.command("visual")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.argument('screenshot_id', type=int)
@click.option('--template', type=click.Choice(list(TEMPLATES)),
              help="A shipped layout: classic, editorial or hero. Or give your own with --jsx-file.")
@click.option('--jsx-file', type=click.Path(exists=True, dir_okay=False),
              help="Your own React component (default export) for the visual.")
@click.option('--props-file', type=click.Path(exists=True, dir_okay=False),
              help="JSON props for the component.")
@click.option('--font', 'font_spec', help="Google Font to embed, e.g. 'Inter:600,800'.")
def visual(key, screenshot_id, template, jsx_file, props_file, font_spec):
    """ Creates or updates the marketing visual for screenshot SCREENSHOT_ID of the app \"KEY\".

    \f
    One visual per screenshot: running this again on the same id updates it in place and resets its
    approval, so it never ships a stale image. The result is visible in the editor after a refresh.

    Usage:
    """
    base = _app_base(key)
    if base:
        _visual(base, screenshot_id, template, jsx_file, props_file, font_spec, "odevio screenshot ls")


def _template_file(template, jsx_file):
    """ The JSX to send: a shipped template by name, or the agent's own file. """
    import os

    from odevio.commands.skill import skill_source

    if bool(template) == bool(jsx_file):
        raise click.UsageError("Give either --template or --jsx-file.")
    if jsx_file:
        return jsx_file
    return os.path.join(skill_source(), "references", "templates", TEMPLATES[template])


def _visual(base, screenshot_id, template, jsx_file, props_file, font_spec, ls_command):
    import json

    from odevio import api
    from odevio.settings import console

    jsx_file = _template_file(template, jsx_file)

    entry = _screenshot_entry(base, screenshot_id)
    if entry is None:
        console.print(f"[warning]No screenshot #{screenshot_id} here.[/warning] "
                      f"Run '{ls_command}' to see the ids.")
        return

    with open(jsx_file) as fh:
        jsx_source = fh.read()
    props = {}
    if props_file:
        with open(props_file) as fh:
            props = json.load(fh)
    payload = {"source_screenshot": screenshot_id, "jsx_source": jsx_source, "props": props}
    if font_spec:
        payload["font"] = _resolve_font(font_spec)

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
@click.argument('screenshot_ids', type=int, nargs=-1, required=True)
@click.option('--out-dir', type=click.Path(file_okay=False), help="Also save each approved PNG in this folder.")
def approve_visual(key, screenshot_ids, out_dir):
    """ Renders and approves the marketing visuals of screenshots SCREENSHOT_IDS of the app \"KEY\".

    \f
    Approving renders the submission PNG and marks the visual as the image that replaces the raw
    screenshot on the App Store. Nothing is sent to Apple until :code:`odevio screenshot push`.

    Usage:
    """
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
    """ Renders the marketing visuals of SCREENSHOT_IDS of the app \"KEY\" as drafts and saves the PNGs.

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

    # Long enough for a capture that hangs, is killed and is retried once on the server.
    for _ in range(100):
        time.sleep(1.5)
        status = api.get(f"/marketing-visuals/{visual_id}/approve-status/{task_id}/") or {}
        if status.get("state") in ("SUCCESS", "FAILURE"):
            return status
    return None


def _save_png(visual_id, out_dir, name):
    """ Download a visual's last render into OUT_DIR, returning the file written. """
    import os
    from urllib.parse import urlparse

    import requests

    from odevio import api
    from odevio.settings import API_BASE_URL

    url = (api.get(f"/marketing-visuals/{visual_id}/") or {}).get("rendered_png")
    if not url:
        return None
    response = requests.get(API_BASE_URL + urlparse(url).path,
                            headers={"Authorization": api.get_authorization_header()})
    response.raise_for_status()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "wb") as handle:
        handle.write(response.content)
    return path


def _render_visuals(base, screenshot_ids, approve, out_dir, visual_command):
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
                          "It will replace the raw screenshot on the next push.")
        else:
            console.print(f"[success]Rendered a draft of #{screenshot_id}.[/success] Not approved: nothing ships yet.")
        if out_dir:
            path = _save_png(visual_id, out_dir, f"{'approved' if approve else 'preview'}-{screenshot_id}.png")
            if path:
                console.print(f"Saved to {path}")


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
def listing_upload(key, files, size):
    """ Adds images to the store listing \"KEY\" — raw captures or finished pictures — at Apple's exact slot size. """
    base = _listing_base(key)
    if base:
        _upload(base, files, size)


@listing.command("visual")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_id', type=int)
@click.option('--template', type=click.Choice(list(TEMPLATES)),
              help="A shipped layout: classic, editorial or hero. Or give your own with --jsx-file.")
@click.option('--jsx-file', type=click.Path(exists=True, dir_okay=False),
              help="Your own React component (default export) for the visual.")
@click.option('--props-file', type=click.Path(exists=True, dir_okay=False),
              help="JSON props for the component.")
@click.option('--font', 'font_spec', help="Google Font to embed, e.g. 'Inter:600,800'.")
def listing_visual(key, screenshot_id, template, jsx_file, props_file, font_spec):
    """ Creates or updates the marketing visual for screenshot SCREENSHOT_ID of the listing \"KEY\". """
    _visual(f"/store-listings/{key}", screenshot_id, template, jsx_file, props_file, font_spec,
            f"odevio screenshot listing screenshots {key}")


@listing.command("approve-visual")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_ids', type=int, nargs=-1, required=True)
@click.option('--out-dir', type=click.Path(file_okay=False), help="Also save each approved PNG in this folder.")
def listing_approve_visual(key, screenshot_ids, out_dir):
    """ Renders and approves the marketing visuals of screenshots SCREENSHOT_IDS of the listing \"KEY\". """
    _render_visuals(f"/store-listings/{key}", screenshot_ids, True, out_dir, "odevio screenshot listing visual")


@listing.command("preview")
@login_required_warning_decorator
@click.argument('key')
@click.argument('screenshot_ids', type=int, nargs=-1, required=True)
@click.option('--out-dir', type=click.Path(file_okay=False), default=".", show_default=True,
              help="Folder the preview PNGs are saved in.")
def listing_preview(key, screenshot_ids, out_dir):
    """ Renders the marketing visuals of SCREENSHOT_IDS of the listing \"KEY\" as drafts and saves the PNGs. """
    _render_visuals(f"/store-listings/{key}", screenshot_ids, False, out_dir, "odevio screenshot listing visual")


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
