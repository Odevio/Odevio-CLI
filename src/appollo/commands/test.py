import click

from appollo.helpers import login_required_warning_decorator

@click.command()
@login_required_warning_decorator
@click.argument('app-key', required=False)
@click.argument('directory', type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),required=False)
@click.option('--path', help="The path to the test you want launch by default 'test' folder.")
@click.option('--extra-test-parameters', help="option to add personal option.")
@click.option('-t', '--tags', help="Run only tests associated with the specified tags.")
@click.option('-x', '--exclude-tags', help="Run only tests that do not have the specified tags.")
def test(path,tags, exclude_tags, extra_test_parameters, app_key=None, directory=None):
    """ Subcommands to launch your application's tests
    """

    import os
    import textwrap

    from rich.text import Text

    from appollo.settings import console
    from appollo.helpers import zip_directory, terminal_menu

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


    # ***
    # call api launch tes
    # ***

    console.print("The test is launched")