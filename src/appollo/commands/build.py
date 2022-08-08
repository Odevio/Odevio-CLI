import click


@click.group('build')
def build():
    """ Subcommands to build an app and track builds.

    \f
    When starting a new project commands are mostly executed in this order :

        1. :code:`appollo build start --build-type="configuration [DIRECTORY]"` to create an Appollo-Remote with the right environment for your application. This will return a key, you will use in the next commands.
        2. :code:`appollo build connect <key>` to get your connection settings and access the Appolo Remote on which you can test and setup your application with XCode.
        3. :code:`appollo build stop <key>` to stop your Appolo Remote when you're done editing your settings.
        4. :code:`appollo build patch <key>` to retrieve the changes made on the Appollo-Remote.
        5. :code:`git am appollo.patch` to apply the changes locally.
        6. :code:`appollo build start [OPTIONS] [DIRECTORY]` to build your app with Flutter and generate an IPA or to publish your app on the App Store.

    Usage:
    """
    pass


@build.command()
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
@click.argument('key', required=True)
def rm(key):
    """ Delete build with key \"KEY\" and its corresponding Appollo-Remote.

    \f

    .. note:: Appollo-Remotes are MacOS build machines on which the flutter build of your application is executed.
    """
    from appollo import api
    from appollo.settings import console

    build_instance = api.delete(f"/builds/{key}/")

    if build_instance:
        console.print(f"Build with KEY {key} has been deleted")


@build.command()
@click.argument('key', required=True)
def detail(key):
    """ Fetches detailed information of build with key \"KEY\".

    Returns the location of the logs and application artifacts.
    """
    import textwrap

    from rich.text import Text
    from rich.panel import Panel
    from rich.syntax import Syntax

    from appollo import api
    from appollo.settings import console

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
@click.argument('directory', type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
                required=False)
@click.option('--app-key', required=True, prompt=True, help="Key of the application to build")
@click.option('--build-type', help="Build type", prompt=True,
              type=click.Choice(["configuration", "development", "ad-hoc", "distribution", "validation", "publication"]))
@click.option('--flutter', help="Flutter version for your build (example \"2.8.1\")",)
@click.option('--minimal-ios-version', help="Minimal iOS version for you application (example \"9.0\")")
@click.option('--app-version', help="App version to set for this build (for example \"1.3.1\"). If not set, the version in pubspec.yaml will be used")
@click.option('--build-number', help="Build number to set for this build (the number after '+' in the version in pubspec.yaml). If not set, the build number in pubspec.yaml will be used")
def start(app_key, build_type, flutter, minimal_ios_version, app_version, build_number, directory=None):
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

    Build start in detached mode you can check the progress of all your Appollo-Remotes by running
    :code:`appollo build ls` or get detailed information by running :code:`appollo build detail <key>`
    """
    import os

    from rich.syntax import Syntax
    from appollo.settings import console
    from appollo.helpers import zip_directory
    from appollo import api

    if directory is None:
        directory = os.getcwd()

    print(f"Zipping {directory}")
    zip_directory(directory)

    print(f"Uploading {directory}")

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

    # TODO show realtime logs and build process.


@build.command()
@click.argument('key', required=True)
def ipa(key):
    """ Get the ipa file of build with key \"KEY\".

    \b
    This command is used when a build of type ad-hoc, ipa, validation or publication has succeeded.
    It returns an url to get the IPA, either to download it, or to install it if opened from an iOS device.
    """
    from appollo import api
    from appollo.settings import console

    response = api.get(f"/builds/{key}/ipa/")

    if response:
        console.print(f"[link={response['url']}]{response['url']}[/link]")
        console.print("Open this url to download the IPA, or with an iOS device to install it.")
    else:
        console.print("This build does not have any IPA")


@build.command()
@click.argument('key', required=True)
@click.option(
    "-o", "--output", default="result.zip", help="Output filename (default: result.zip)",
    type=click.Path(exists=False, resolve_path=True, file_okay=True, dir_okay=False))
def result(key, output="result.zip"):
    """ Get the modified sources of build with key \"KEY\".

    \b
    This command is used when a build is finished to retrieved its entire directory on the remote machine.
    """
    from appollo import api
    from appollo.settings import console

    response = api.get(f"/builds/{key}/result/", json_decode=False)

    if response:
        with open(output, "wb") as f:
            f.write(response)
    else:
        console.print("This build does not have any result")


@build.command()
@click.argument('key', required=True)
@click.option("-y", "--yes", is_flag=True, help="Automatically create an Appollo Remote if your build was not setup for remote desktop", )
def connect(key, yes):
    """ Get the connection information for an Appollo-Remote linked to build with key \"KEY\".

    \b
    This command is mainly used when it is needed to connect to the Appollo-Remote with a Remote Desktop client :
        - Xcode configuration
        - Debugging and detailed log analysis
        - Correcting code and restarting a build after failure
        - Testing the application on the iPhone or iPad simulator.

    \f
    This command will start an Appollo-Remote and return connection settings and credentials for you to connect with a
    remote desktop client to the Appollo-Remote.

    .. note:: Appollo-Remotes are MacOS build machines on which the flutter build of your application is executed.
    .. note:: The connection uses spice protocol, your Remote DEsktop must support it to allow you to use an Appollo Remote
    """
    import textwrap

    from rich.panel import Panel
    from rich.text import Text
    from rich.syntax import Syntax

    from appollo.settings import console

    from appollo import api

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
            console.print("Your VM is currently prepared for being used as Remote Desktop. Please try again in a few moments.")
        else:
            auth_info = Panel(Text.from_markup(
                textwrap.dedent(
                    f"""
                        url: [bold]spice://appollo.deuse.dev:{build_instance["remote_desktop_port"]}[/bold]
                        connection_password: [bold]{build_instance["remote_desktop_password"]}[/bold]
                        user: [bold]appollo[/bold]
                        user_password: [bold]{build_instance["vm_password"]}[/bold]
                    """
                )
            ), title="Connexion settings and credentials", expand=False)
            console.print(auth_info)
            console.print("Most Remote Desktop applications link the Mac Command key to Windows key on your keyboard.")
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
@click.argument('key', required=True)
@click.option(
    "-o", "--output", default="appollo.patch", help="Output filename (default: appollo.patch)",
    type=click.Path(exists=False, resolve_path=True, file_okay=True, dir_okay=False))
def patch(key, output="result.zip"):
    """ Retrieve a patch that gathers all changes made to the source code of build with key \"KEY\".

    \b
    This command is used when a build is finished and succeeded or when you have stopped an Appollo Remote on which you configured an app with XCode.

    .. note:: The patch was made on a blank Git repo.
    """
    from rich.syntax import Syntax

    from appollo.settings import console
    from appollo import api

    response = api.get(f"/builds/{key}/patch/", json_decode=False)

    if response:
        with open(output, "wb") as f:
            f.write(response)
    else:
        console.print("This build does not have any patch")

    code = Syntax("git am appollo.patch", lexer="shell")
    console.print("To apply a patch, run")
    console.print(code)


@build.command()
@click.argument('key', required=True)
def stop(key):
    """ Stops running build KEY """
    from rich.text import Text

    from appollo.settings import console
    from appollo import api

    build_instance = api.post(f"/builds/{key}/stop/")
    if build_instance:
        console.print(Text.from_markup(f"[bold]{build_instance['name']}[/bold] has been stopped."))
    else:
        console.print(f"Build with KEY \"{key}\" was not found.")


@build.command()
@click.argument('key', required=True)
def logs(key):
    """
    Outputs the logs of build KEY

    .. note:: Logs are printed only when a command has finished its execution. In particular, Flutter logs are only printed when the flutter command execution has ended.
    """
    from appollo.settings import console
    from appollo import api

    logs = api.get(f"/builds/{key}/logs/")
    console.print(logs)

# TODO Commandes pour lister les versions Flutter disponibles
