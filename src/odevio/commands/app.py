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
        console.print("You did not register any app identifiers. Create one with")
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
                                        """
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
                                        """
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


@app.command("store-status")
@login_required_warning_decorator
@click.argument('key', required=False)
def store_status(key):
    """ Shows what the App Store listing of the app with key \"KEY\" still needs.

    \f
    The answer is read from Apple every time rather than remembered, so it stays right even when the
    listing was edited in App Store Connect since the last run, or from another machine. Filling an App
    Store page rarely happens in one sitting, and this is what makes it possible to stop and come back.

    It also prints the copy the listing already holds - name, subtitle, keywords, promotional text and
    description - so weak or thin text can be read and improved, not just checked for being present.

    One thing cannot be checked: Apple offers no way to read the App Privacy answers, so they are always
    listed as something to confirm rather than reported as done or missing.

    Usage:
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return
    try:
        status = api.get(f"/applications/{key}/store-status/")
    except api.NotFoundException:
        console.print("This key is invalid or you do not have access to it.")
        return
    if not status:
        return

    if not status.get("listing_exists"):
        console.print(f"[warning]{status['bundle_id']} has no App Store listing yet.[/warning]")
        console.print("Create it once on [link]https://appstoreconnect.apple.com[/link] — Apple does not "
                      "allow an app to be created any other way.")
        return

    console.print(f"[title]{status['name']}[/title]  version {status.get('version') or '-'}"
                  f"  ({status.get('version_state', 'unknown state')})")
    console.print(f"Listing language: [code]{status['locale']}[/code]")
    screenshots_by_slot = status.get("screenshots") or {}
    if screenshots_by_slot:
        console.print("Screenshots: " + ", ".join(
            f"{count} for {slot}" for slot, count in sorted(screenshots_by_slot.items())))
    console.print(f"Build on the page: {status.get('build') or 'none yet'}")

    # The copy Apple holds, so it can be read and improved rather than only checked for presence. Older
    # servers do not send it; then this block is simply skipped.
    texts = status.get("texts") or {}
    present = [
        (label, texts.get(field))
        for label, field in (
            ("Name", "name"),
            ("Subtitle", "subtitle"),
            ("Keywords", "keywords"),
            ("Promotional text", "promotional_text"),
            ("Description", "description"),
        )
        if texts.get(field)
    ]
    if present:
        console.print("")
        console.print("[title]Current copy[/title]")
        for label, value in present:
            console.print(f"  [code]{label}[/code]: {value}")

    available = status.get("available_builds") or []
    if available:
        console.print("")
        console.print("[title]Builds Apple holds[/title]")
        for item in available:
            state = item["state"]
            if item["expired"]:
                state = "expired"
            console.print(f"  {item['version']:<8} {str(item['uploaded'])[:10]}  {state}")
    console.print("")

    if status.get("missing"):
        console.print("[title]Still to do[/title]")
        for item in status["missing"]:
            console.print(f"  - {item}")
    else:
        console.print("[success]Nothing left to fill in.[/success]")


@app.command("set-metadata")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--description', help="What the app does, as shown on its App Store page. 4000 characters.")
@click.option('--description-file', type=click.Path(exists=True, dir_okay=False),
              help="Read the description from a file instead. Better for anything with line breaks.")
@click.option('--keywords', help="Comma separated, 100 characters in total for all of them.")
@click.option('--name', help="The public name on the App Store. 30 characters, unique across the store.")
@click.option('--subtitle', help="One line under the app name. 30 characters.")
@click.option('--promotional-text', help="170 characters, changeable without a new version.")
@click.option('--release-notes',
              help='"What\'s New" for an update - what changed since the last version. For updates only; '
                   'Apple refuses it on a first version.')
@click.option('--release-notes-file', type=click.Path(exists=True, dir_okay=False),
              help="Read the release notes from a file instead. Better for anything with line breaks.")
@click.option('--support-url', help="A page where people can get help. Apple checks that it answers.")
@click.option('--marketing-url', help="The app's own web page, if it has one.")
@click.option('--privacy-policy-url', help="A page saying what the app does with people's data.")
@click.option('--copyright', help='For example "2026 Acme".')
@click.option('--contact-first-name', help="Given name of whoever Apple should contact about the review.")
@click.option('--contact-last-name', help="Family name of the same person.")
@click.option('--contact-email', help="Their email. Apple wants all four contact options together.")
@click.option('--contact-phone', help='With the country code, for example "+32 496 00 00 00".')
@click.option('--demo-account-name', help="Login Apple's reviewer should use, if the app needs one.")
@click.option('--demo-account-password', help="Its password. Apple refuses an app it cannot get into.")
@click.option('--review-notes',
              help="Notes for Apple's reviewer - anything they need to know to test the app.")
@click.option('--review-notes-file', type=click.Path(exists=True, dir_okay=False),
              help="Read the review notes from a file instead. Better for anything with line breaks.")
@click.option('--uses-third-party-content', type=bool, default=None,
              help="Whether the app contains anything made by someone else.")
@click.option('--category', help="Apple category the app is filed under. See 'odevio app categories'.")
@click.option('--free', is_flag=True, help="Make the app free. Apple requires a price even when it is none.")
@click.option('--price',
              help='Set a paid price, for example "4.99", matched to Apple\'s USA prices. Use --free '
                   'instead for a free app.')
@click.option('--age-rating', is_flag=True,
              help="Answer the age rating questionnaire as containing nothing objectionable.")
def set_metadata(key, **fields):
    """ Writes the App Store page of the app with key \"KEY\".

    \f
    Only what you pass is written; everything else is left as Apple holds it. So this can be run again as
    the text takes shape, rather than having to be complete the first time.

    Apple enforces the lengths exactly and refuses the whole request when one is exceeded: 30 characters
    for the subtitle, 4000 for the description, 100 for all the keywords together, 170 for the
    promotional text.

    Usage:
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return

    # A description runs to paragraphs, and a paragraph on a command line means quoting line breaks,
    # apostrophes and bullets through the shell. Reading it from a file avoids all of that.
    description_file = fields.pop("description_file", None)
    if description_file:
        if fields.get("description"):
            console.print("Pass either --description or --description-file, not both.")
            return
        with open(description_file, encoding="utf-8") as handle:
            fields["description"] = handle.read().strip()

    # Review notes run to several lines just like a description, so the same file option avoids quoting
    # line breaks through the shell.
    review_notes_file = fields.pop("review_notes_file", None)
    if review_notes_file:
        if fields.get("review_notes"):
            console.print("Pass either --review-notes or --review-notes-file, not both.")
            return
        with open(review_notes_file, encoding="utf-8") as handle:
            fields["review_notes"] = handle.read().strip()

    # "What's New" is another multi-line field, so it gets the same file option.
    release_notes_file = fields.pop("release_notes_file", None)
    if release_notes_file:
        if fields.get("release_notes"):
            console.print("Pass either --release-notes or --release-notes-file, not both.")
            return
        with open(release_notes_file, encoding="utf-8") as handle:
            fields["release_notes"] = handle.read().strip()

    if fields.get("price") and fields.get("free"):
        console.print("Pass either --free or --price, not both.")
        return

    # False is dropped for the switches, whose "off" only means the user did not pass them, but kept
    # for anything that genuinely has two values. Dropping it everywhere made
    # --uses-third-party-content false do nothing at all, while true went through — so the one answer
    # Apple needs from almost every app was the one that could not be given.
    switches = ("free", "age_rating")
    data = {name: value for name, value in fields.items()
            if value is not None and not (name in switches and value is False)}
    if data.get("demo_account_name"):
        data["demo_account_required"] = 1
    if not data:
        console.print("Nothing to write — pass at least one of the options. See --help.")
        return

    result = api.post(f"/applications/{key}/set-metadata/", json_data=data)
    if not result:
        return

    written = result.get("written") or []
    console.print(f"[success]Written to your App Store page:[/success] {', '.join(written)}"
                  if written else "Nothing needed changing.")

    # Apple takes a whole block or none of it, so one bad value loses everything sent beside it. Saying
    # which block did not land, and why, is the difference between fixing one field and believing the
    # whole command worked.
    for label, problem in (result.get("failed") or {}).items():
        console.print(f"[warning]Apple refused the {label}:[/warning] {problem}")
        console.print(f"Nothing of the {label} was saved. Correct it and pass those options again.")

    # Apple opens these pages during the review, so a link that does not answer is a refusal several days
    # from now. Saying so while the address is still in front of the user costs nothing.
    for label, problem in (result.get("url_warnings") or {}).items():
        console.print(f"[warning]The {label} address does not work:[/warning] {problem}")


@app.command("categories")
@login_required_warning_decorator
@click.argument('key', required=False)
def categories(key):
    """ Lists the App Store categories the app with key \"KEY\" can be filed under. """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return
    listed = api.get(f"/applications/{key}/categories/")
    if listed:
        for item in listed:
            console.print(f"  {item['name']:<28} [code]{item['id']}[/code]")


@app.command("attach-build")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--build-number',
              help='Build number (CFBundleVersion) to attach, as listed under "Builds Apple holds" by '
                   'store-status. Defaults to the most recent usable build.')
@click.option('--version', hidden=True,
              help="Deprecated: use --build-number. Kept for existing scripts.")
def attach_build(key, build_number, version):
    """ Points the App Store page of the app with key \"KEY\" at an uploaded build.

    \f
    Sending a build and choosing it for a version are two different things. Apple takes between a few
    minutes and half an hour to examine what was sent, and only then can it be attached — until then the
    page looks complete but cannot be submitted.

    Rather than wait, this command can simply be run again: it either attaches a build or tells you what
    it is waiting for.

    Without :code:`--build-number` the most recent usable build is attached. Pass it to choose a specific
    build by its build number - the sequential value :code:`store-status` lists under "Builds Apple holds".

    Usage:
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return
    data = {}
    if build_number:
        data["build_number"] = build_number
    if version:
        data["version"] = version
    try:
        result = api.post(f"/applications/{key}/attach-build/", json_data=data)
    except api.NotFoundException:
        console.print("This key is invalid or you do not have access to it.")
        return
    if not result:
        return

    if result.get("attached"):
        if result.get("already"):
            console.print(f"[success]Build {result.get('build')} was already attached.[/success]")
        elif result.get("replaced"):
            console.print(f"[success]Build {result.get('build')} is now attached to your App Store "
                          f"page[/success], replacing {result.get('replaced')}.")
        else:
            console.print(f"[success]Build {result.get('build')} is now attached to your App Store "
                          f"page.[/success]")
    else:
        console.print(f"[warning]{result.get('waiting')}[/warning]")


@app.command("submit")
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option('--confirm', is_flag=True,
              help="Required. Sending for review cannot be undone, so it is never implied.")
def submit(key, confirm):
    """ Sends the App Store page of the app with key \"KEY\" to Apple for review.

    \f
    The point of no return. A human at Apple looks at the app from here, and nothing on the page can be
    changed until they answer, which usually takes a day or two.

    :code:`--confirm` is required rather than a question being asked, so that this can never happen as a
    side effect of a script and never depends on a terminal being there to answer.

    Apple is asked once more whether the version is acceptable before it goes, so an incomplete page is
    reported back instead of being sent.

    Usage:
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return
    if not confirm:
        console.print("[warning]Nothing was sent.[/warning] Sending for review cannot be undone: a "
                      "reviewer at Apple looks at your app and the page is frozen until they answer.")
        console.print("Run it again with [code]--confirm[/code] when you mean it.")
        return
    try:
        answer = api.post(f"/applications/{key}/submit/", json_data={})
    except api.NotFoundException:
        console.print("This key is invalid or you do not have access to it.")
        return
    if not answer:
        return

    if answer.get("submitted"):
        console.print(f"[success]Version {answer.get('version')} is with Apple's reviewers.[/success]")
        console.print("They usually answer within a day or two. The page cannot be changed until then.")
    elif answer.get("already_sent"):
        console.print(f"[success]Version {answer.get('version')} is already with Apple.[/success]")
        console.print("Nothing more to send; they answer within a day or two.")
    else:
        console.print("[warning]Not sent — Apple still wants:[/warning]")
        for detail in answer.get("blockers") or []:
            console.print(f"  {detail}")


@app.command("check-submittable")
@login_required_warning_decorator
@click.argument('key', required=False)
def check_submittable(key):
    """ Asks Apple whether the App Store page of the app with key \"KEY\" is ready to submit.

    \f
    This is Apple's own verdict rather than ours, so it is the one to trust — including which screenshot
    sizes this particular app has to provide, which Apple states nowhere else.

    It leaves a trace, which is why it is separate from :code:`store-status`. The only way to obtain the
    answer is to offer Apple the version, and that opens a review submission which cannot afterwards be
    deleted. It is reused rather than duplicated, and becomes the submission the app is released with, so
    run it when you mean to finish rather than to check on progress.

    Nothing is submitted: the app is only offered for inspection. Sending it for review stays a separate,
    deliberate act.

    Usage:
    """
    from odevio import api
    from odevio.helpers import terminal_menu
    from odevio.settings import console

    if key is None:
        key = terminal_menu("/applications/", "Application",
                            does_not_exist_msg="You do not have any app identifiers.")
        if key is None:
            return
    try:
        answer = api.post(f"/applications/{key}/check-submittable/", json_data={})
    except api.NotFoundException:
        console.print("This key is invalid or you do not have access to it.")
        return
    if not answer:
        return

    if answer.get("ready"):
        console.print("[success]Apple says this version is ready to submit.[/success]")
        console.print("Nothing is sent yet — submitting stays a separate step.")
        return

    console.print("[title]Apple is still waiting for[/title]")
    for item in answer.get("missing", []):
        console.print(f"  - {item}")
    required = answer.get("required_screenshots")
    if required:
        console.print("")
        console.print("Screenshot sizes this app must provide: "
                      f"[code]{', '.join(required)}[/code]")
        