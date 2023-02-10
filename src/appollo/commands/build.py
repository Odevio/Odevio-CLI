import click

from appollo.helpers import login_required_warning_decorator


@click.group('build')
def build():
    """ Subcommands to build an app and track builds.

    \f
    When starting a new project commands are mostly executed in this order :

        1. :code:`appollo build start --build-type="configuration [DIRECTORY]"` to create an Appollo-Remote with the right environment for your application.
        2. :code:`appollo build connect` to get your connection settings and access the Appolo Remote on which you can test and setup your application with XCode.
        3. :code:`appollo build stop` to stop your Appolo Remote when you're done editing your settings.
        4. :code:`appollo build patch` to retrieve the changes made on the Appollo-Remote.
        5. :code:`git am appollo.patch` to apply the changes locally.
        6. :code:`appollo build start [OPTIONS]`
        
    Usage:
    """
    pass


@build.command()
@login_required_warning_decorator
@click.option('-a', '--all', 'show_all', default=False, is_flag=True,
              help="shows your builds and the builds from your teams")
def ls(show_all):
    """ Lists builds on Appollo. """
    from rich.table import Table
    from rich.syntax import Syntax

    from appollo import api
    from appollo.settings import console

    if show_all:
        builds = api.get("/builds/", params={"all": 1})
    else:
        builds = api.get("/builds/")

    if builds:
        table = Table()
        table.add_column("KEY")
        table.add_column("App")
        table.add_column("Name")
        table.add_column("Started at")
        table.add_column("Finished at")
        table.add_column("Status")
        table.add_column("Build Type")
        table.add_column("Started by")
        table.add_column("Certificate")
        table.add_column("Profile")

        for b in builds:
            table.add_row(b['key'], b['application'], b['name'], b['start_time'],
                          b['finish_time'], b['status'], b['build_type'], b['creator'],
                          b['certificate'], b['profile'])

        console.print(table)
    else:
        if show_all:
            code = Syntax(code="$ appollo build start SOURCE_DIRECTORY --app-key APPLICATION_KEY", lexer="shell")
            console.print(f"You did not launch any builds. Create one with")
            console.print(code)
        else:
            code = Syntax(code="$ appollo build ls --all", lexer="shell")
            console.print(f"You do not have any active builds. See all your builds with")
            console.print(code)


@build.command()
@login_required_warning_decorator
@click.argument('key', required=False)
def rm(key):
    """ Deletes a build and its corresponding Appollo-Remote.

    \f

    .. note:: Appollo-Remotes are MacOS build machines on which the flutter build of your application is executed.
    """
    import textwrap

    from rich.text import Text

    from appollo import api
    from appollo.settings import console
    from appollo.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/builds/", "Builds", api_params={"all": 1}, name=build_name,
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You have not run any builds yet.
                                        """
                                    )))
        if key is None:
            return

    build_instance = api.delete(f"/builds/{key}/")

    if build_instance:
        console.print(f"Build with KEY {key} has been deleted")


@build.command()
@login_required_warning_decorator
@click.argument('key', required=False)
def detail(key):
    """ Fetches detailed information of a build.

    Returns the location of the logs and application artifacts.
    """
    import textwrap

    from rich.text import Text
    from rich.panel import Panel
    from rich.syntax import Syntax

    from appollo import api
    from appollo.settings import console
    from appollo.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/builds/", "Builds", api_params={"all": 1}, name=build_name,
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You have not run any builds yet.
                                        """
                                    )))
        if key is None:
            return

    build_instance = api.get(f"/builds/{key}/")

    if build_instance:
        console.print(Panel(Text.from_markup(
            textwrap.dedent(
                f"""
                Appollo Key : [bold]{build_instance["key"]}[/bold]
                Name : [bold]{build_instance["name"]}[/bold]
                Application : [bold]{build_instance["application"]}[/bold]
                Status : [bold]{build_instance["status"] + (" - " + build_instance["substatus"] if build_instance["substatus"] else "")}[/bold]
                Remote Desktop status : [bold]{build_instance["remote_desktop_status"]}[/bold]
                Creator : [bold]{build_instance["creator"]}[/bold]
                """
            )
        ), title="General information"))

        console.print(Panel(Text.from_markup(
            textwrap.dedent(
                f"""
                Flutter version: [bold]{build_instance["flutter_version"]}[/bold]
                Build type : [bold]{build_instance["build_type"]}[/bold]
                Provisioning profile : [bold]{build_instance["profile"]}[/bold]
                Certificate : [bold]{build_instance["certificate"]}[/bold]
                Minimum iOS SDK : [bold]{build_instance["min_sdk"]}[/bold]
                App version: [bold]{build_instance["app_version"] or "-"}[/bold]
                Build number: [bold]{build_instance["build_number"] or "-"}[/bold]
                """
            )
        ), title="Build config"))

        if build_instance.get("error_message"):
            console.print(Panel(Text.from_markup(
                textwrap.dedent(
                    f"""
                    Error message: [bold]{build_instance['error_message']}[/bold]
                    """
                )
            ), title="Error details"))
            # TODO Add errors codes in doc

        code = Syntax(f"appollo build logs {key}", lexer="shell")
        console.print("To see logs of this build, run")
        console.print(code)
    else:
        console.print("This build was not found or you cannot access it.")


@build.command()
@login_required_warning_decorator
@click.argument('app-key', required=False)
@click.argument('directory', type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
                required=False)
@click.option('--build-type', help="Build type", prompt=True,
              type=click.Choice(["configuration", "development", "ad-hoc", "distribution", "validation", "publication", "test"]))
@click.option('--flutter', help="Flutter version for your build (example \"2.8.1\"). Use appollo build flutter-versions to see all available versions",)
@click.option('--minimal-ios-version', help="Minimal iOS version for you application (example \"9.0\")")
@click.option('--app-version', help="App version to set for this build (for example \"1.3.1\"). If not set, the version in pubspec.yaml will be used")
@click.option('--build-number', help="Build number to set for this build (the number after '+' in the version in pubspec.yaml). If not set, the build number in pubspec.yaml will be used")
@click.option('--no-progress', is_flag=True, help="Do not display the progress and exit the command immediately.")
def start(build_type, flutter, minimal_ios_version, app_version, build_number, no_progress, app_key=None, directory=None):
    """ Start a new build from scratch

    DIRECTORY : Home directory of the flutter project. If not provided gets the current directory.

    \f
    The Appollo tool is composed of :

        - *Appollo-Remote* : The pre-configured build machines which handle the setup, build and release of your app
        - *Appollo-cli* : The CLI command line that works as an interface to start Appollo-Remote build machines

    :code:`appollo build start [DIRECTORY] --build-type <build-type>` creates an Appollo-Remote and builds the app
    either for development, ad-hoc, distribution, validation or publication

        * **Configuration**: launch an Appollo-Remote to allow you to configure your project on XCode
        * **Development** : builds the app for testing on an iOS simulator.
        * **Ad-hoc** : Build an .ipa file for testing on the devices listed in your developer account. For the list of
          devices check :code:`appollo apple detail <apple-dev-account-key>`.
        * **Distribution** : Build an .ipa file that can be distributed on any device.
        * **Validation** : Build an .ipa file and validates that it can be released on the App Store.
        * **Publication** : Build an .ipa file and publish it on the App Store. Once this build succeeds you have
          to go on the App Store to complete information and screenshots related to your new application version.

    Killing this command will not stop the build you can check the progress of all your Appollo-Remotes by running
    :code:`appollo build ls` or get detailed information by running :code:`appollo build detail` and selecting your build.
    """
    import os
    import textwrap
    from time import sleep

    from rich.text import Text
    from rich.syntax import Syntax

    from appollo.settings import console
    from appollo.helpers import zip_directory, terminal_menu
    from appollo import api

    if directory is None:
        directory = os.getcwd()

    if not os.path.exists(os.path.join(directory, "lib")) or not os.path.exists(os.path.join(directory, "pubspec.yaml")):
        res = console.input("This directory does not look like it contains a flutter project. Are you sure you want to upload it? (y/N) ")
        if res not in ["y", "Y"]:
            return

    if app_key is None:
        app_key = terminal_menu("/applications/", "Application",
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You have no app identifiers in your account. Check out [code]$ appollo app mk [/code] to create an app identifier.
                                        """
                                    )))
        if app_key is None:
            return

    console.print(f"Zipping {directory}")
    zip_file = zip_directory(directory)

    file_size_mb = round(os.path.getsize(zip_file)/1000000, 2)

    if file_size_mb > 1000:
        console.print("File size exceeds 1GB, very large applications are not supported by Appollo.")
        return

    console.print(f"Uploading {directory} ({file_size_mb} MB)")

    build_instance = api.post(
        "/builds/",
        json_data={
            "application": app_key,
            "build_type": build_type,
            "min_sdk": minimal_ios_version,
            "flutter_version": flutter,
            "app_version": app_version,
            "build_number": build_number,
        },
        files={
            "source": ("source.zip", open(".app.zip", "rb"), "application/zip")
        },
    )

    os.remove(".app.zip")

    if build_instance:
        console.print(f"{build_instance['name']} has been registered. It has key \"{build_instance['key']}\" "
                      f"and will be started as soon as possible.")
        if build_type == "configuration":
            code = Syntax(code=f"appollo build connect {build_instance['key']}", lexer="shell")
            console.print("To access your Appollo-Remote, you can use the following command when it has been started.")
            console.print(code)
        console.print("Killing the command will not stop the build.")

        if no_progress:
            return

        # check build progress.
        loop = True
        with console.status("Waiting for available instance...", spinner="line") as spinner:
            while loop:
                # update status every 10 second.
                sleep(10)
                build_instance = api.get(f"/builds/{build_instance['key']}/")

                status = build_instance["status_code"]
                if status == "created" or status == "waiting_instance":
                    spinner.update("Waiting for available instance...")
                elif status == "in_progress":
                    substatus = build_instance["substatus_code"]
                    if substatus == "starting_instance":
                        spinner.update("Starting instance...")
                    elif substatus == "preparing_build":
                        spinner.update("Preparing build...")
                    elif substatus == "getting_result":
                        spinner.update("Getting result...")
                    elif substatus == "publishing":
                        spinner.update("Publishing...")
                    else:
                        spinner.update("Building...")
                elif status == "config":
                    spinner.update("Configured for remote access")
                    loop = False
                elif status == "succeeded":
                    spinner.update("Success!")
                    loop = False
                elif status == "failed":
                    spinner.update("Failed")
                    loop = False
                elif status == "stopped":
                    spinner.update("Stopped")
                    loop = False

        if status in ["config", "succeeded"]:
            console.print(Text.from_markup(f"Your build has succeeded"))
            if build_type == "publication":
                console.print("It will appear on your appstoreconnect account shortly")

            if build_type == "ad-hoc":
                ipa({build_instance['key']})
          
            if status == "config":
                connect({build_instance['key']})
            return
        elif status in ["failed", "stopped"]:
            console.print(Text.from_markup(f"Your build has failed, to access logs run : [code]appollo build logs {build_instance['key']}[/code]"))
            exit(1)

@build.command()
@login_required_warning_decorator
@click.argument('key', required=False)
def ipa(key):
    """ Get the ipa file of a build.

    \b
    This command is used when a build of type ad-hoc, ipa, validation or publication has succeeded.
    It returns an url to get the IPA, either to download it, or to install it if opened from an iOS device.
    """
    import textwrap

    from rich.text import Text

    from appollo import api
    from appollo.settings import console
    from appollo.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/builds/", "Builds", api_params={"all": 1}, name=build_name,
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You have not run any builds yet.
                                        """
                                    )))
        if key is None:
            return

    response = api.get(f"/builds/{key}/ipa/")

    if response:
        console.print(f"[link={response['url']}]{response['url']}[/link]")
        console.print("Open this url to download the IPA, or with an iOS device to install it.")
    else:
        console.print("This build does not have any IPA")


@build.command()
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option(
    "-o", "--output", default="source.zip", help="Output filename (default: source.zip)",
    type=click.Path(exists=False, resolve_path=True, file_okay=True, dir_okay=False))
def download(key, output="source.zip"):
    """ Get the modified source code of a build.

    \b
    This command is used when a build is finished or stopped to retrieve its entire directory on the remote machine.
    """
    import textwrap

    from rich.text import Text

    from appollo import api
    from appollo.settings import console
    from appollo.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/builds/", "Builds", api_params={"all": 1}, name=build_name,
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You have not run any builds yet.
                                        """
                                    )))
        if key is None:
            return

    console.print("Downloading modified sources...")
    response = api.get(f"/builds/{key}/result/", json_decode=False)
    console.print("The modified sources have been downloaded and are in source.zip")

    if response:
        with open(output, "wb") as f:
            f.write(response)
    else:
        console.print("Could not download the source code. Are you sure the build is stopped ?")


@build.command()
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option("-y", "--yes", is_flag=True, help="Automatically create an Appollo Remote if your build was not setup for remote desktop", )
def connect(key, yes):
    """ Get the connection information for an Appollo-Remote linked to a build.

    \b
    This command is mainly used when it is needed to connect to the Appollo-Remote with a Remote Desktop client :
        - Xcode configuration
        - Debugging and detailed log analysis
        - Correcting code and restarting a build after failure
        - Testing the application on the iPhone or iPad simulator.

    \f
    This command will start an Appollo-Remote and return connection settings and credentials for you to connect with a
    remote desktop client to the Appollo-Remote.

    .. note:: Appollo-Remotes are active for 30 minutes before being closed automatically.
    .. note:: Appollo-Remotes are MacOS build machines on which the flutter build of your application is executed.
    .. note:: The connection uses the spice protocol, your Remote Desktop client must support it to allow you to use an Appollo-Remote.
    """
    import textwrap

    from rich.panel import Panel
    from rich.text import Text
    from rich.syntax import Syntax

    from appollo.settings import console
    from appollo.helpers import terminal_menu
    from appollo import api

    if key is None:
        key = terminal_menu("/builds/", "Builds", name=build_name,
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You have not run any builds yet.
                                        """
                                    )))
        if key is None:
            return

    build_instance = api.get(f"/builds/{key}/connect/")

    if build_instance:
        if build_instance["remote_desktop_status"] == "no_remote_desktop":
            console.print("This build was not setup for remote desktop.")
            if yes or click.confirm("Do you want to create a copy of this build setup for Remote Desktop access ?", default=False):
                rebuild_instance = api.post(
                    f"/builds/{key}/rebuild/",
                    json_data={
                        "remote_desktop_enabled": True,
                    })

                if rebuild_instance:
                    console.print(f"{rebuild_instance['name']} has been registered. It has key \"{rebuild_instance['key']}\" "
                                  f"and will be started as soon as possible. When it is ready, you will be able to access it "
                                  "with the following command")
                    code = Syntax(code=f"appollo build connect {rebuild_instance['key']}", lexer="shell")
                    console.print(code)

        elif build_instance["remote_desktop_status"] == "remote_desktop_preparation":
            console.print("Your Appollo-Remote is currently prepared for being used as Remote Desktop. Please try again in a few moments.")
        else:
            auth_info = Panel(Text.from_markup(
                textwrap.dedent(
                    f"""
                        url: [bold]spice://appollo.space:{build_instance["remote_desktop_port"]}[/bold]
                        connection_password: [bold]{build_instance["remote_desktop_password"]}[/bold]
                        user: [bold]appollo[/bold]
                        user_password: [bold]{build_instance["vm_password"]}[/bold]
                    """
                )
            ), title="Connexion settings and credentials", expand=False)
            console.print(auth_info)
            console.print("Most Remote Desktop applications link the Mac Command key to the Windows key on your keyboard.")
            open_info = Text.from_markup(
                textwrap.dedent(
                    """
                        Your app is located in [bold]Documents/app[/bold].
                        To configure it with XCode,
                        1. Open [bold]XCode[/bold]
                        2. Select [bold]Open an existing project[/bold]
                        3. Select file [bold]Documents/app/ios/Runner.xcworkspace[/bold]
                        4. Enjoy !
                    """
                ))
            console.print(open_info)


@build.command()
@login_required_warning_decorator
@click.argument('key', required=False)
@click.option(
    "-o", "--output", default="appollo.patch", help="Output filename (default: appollo.patch)",
    type=click.Path(exists=False, resolve_path=True, file_okay=True, dir_okay=False))
def patch(key, output="appollo.patch"):
    """ Retrieve a patch that gathers all changes made to the source code of a build.

    \b
    This command is used when a build is finished and succeeded or when you have stopped an Appollo Remote on which you configured an app with XCode.

    .. note:: The patch was made on a blank Git repo.
    """
    import textwrap

    from rich.text import Text
    from rich.syntax import Syntax

    from appollo.settings import console
    from appollo import api
    from appollo.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/builds/", "Builds", name=build_name, api_params={"all": 1},
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You have not run any builds yet.
                                        """
                                    )))
        if key is None:
            return

    console.print(f"Downloading patch file as {output}.")
    response = api.get(f"/builds/{key}/patch/", json_decode=False)

    if response:
        with open(output, "wb") as f:
            f.write(response)
    else:
        console.print("This build does not have any patch")
        return

    code = Syntax("git am appollo.patch", lexer="shell")
    console.print("To apply a patch, run")
    console.print(code)


@build.command()
@login_required_warning_decorator
@click.argument('key', required=False)
def stop(key):
    """ Stops a running build"""
    import textwrap

    from rich.text import Text

    from appollo.settings import console
    from appollo import api
    from appollo.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/builds/", "Builds", name=build_name,
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You do not have any running builds.
                                        """
                                    )))
        if key is None:
            return

    build_instance = api.post(f"/builds/{key}/stop/")
    if build_instance:
        console.print(Text.from_markup(f"[bold]{build_instance['name']}[/bold] has been stopped."))
    else:
        console.print(f"Build with KEY \"{key}\" was not found.")


@build.command()
@login_required_warning_decorator
@click.argument('key', required=False)
def logs(key):
    """ Outputs the logs of a build

    \f
    .. note:: Logs are printed only when a command has finished its execution. In particular, Flutter logs are only printed when the flutter command execution has ended.
    """
    import textwrap

    from rich.text import Text

    from appollo.settings import console
    from appollo import api
    from appollo.helpers import terminal_menu

    if key is None:
        key = terminal_menu("/builds/", "Builds", name=build_name, api_params={"all": 1},
                                    does_not_exist_msg=Text.from_markup(textwrap.dedent(
                                        f"""
                                            You have not run any builds yet.
                                        """
                                    )))
        if key is None:
            return

    logs = api.get(f"/builds/{key}/logs/")
    console.print(logs)


def build_name(build_instance):
    """ Based on a build instance returns a user friendly name for the build. """
    from datetime import datetime

    if "start_time" in build_instance and build_instance["start_time"]:
        build_instance['start_time'] = build_instance['start_time'][:-3]+build_instance['start_time'][-2:]  # Remove timezone ':' otherwise it can't parse
        start_time = datetime.strptime(build_instance['start_time'], "%Y-%m-%dT%H:%M:%S.%f%z")
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M')
    else:
        start_time_str = "Not started"

    # TODO check if timezones are respected.
    return f"{build_instance['application']} - {build_instance['name']} - {start_time_str}"


@build.command()
@login_required_warning_decorator
def flutter_versions():
    """ Lists the Flutter versions available on Appollo. """
    from rich.columns import Columns

    from appollo import api
    from appollo.settings import console

    versions = api.get("/flutter-versions/")

    if versions:
        columns = Columns(versions, padding=(0, 3), equal=True, title="Flutter versions available")
        console.print(columns)
