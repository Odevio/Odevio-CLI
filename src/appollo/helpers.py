import os
import shutil
from functools import update_wrapper

import click

from appollo.settings import console, get_jwt_token


def zip_directory(directory_path):
    """ Archives a directory in a zip file and returns his name."""
    return shutil.make_archive(os.path.join(os.getcwd(), '.app'), "zip", directory_path)



def print_validation_error(console, response_dict):
    """ Pretty print helper for validation errors in the console"""
    error = response_dict.pop('non_field_errors', None)
    if error is not None:
        console.print(f"Error: {error}")
    for field, errors in response_dict.items():
        if errors is str:
            console.print(f"Error: for {field} - {list(errors)}")
        else:
            console.print(f"Error: for {field} - {errors}")


def login_required_warning_decorator(f):
    # Shows a warning message if the user is not logged in.
    # Check if the user is logged in (if there is a JWT token we make the assumption that the user is logged in).
    # If he is not logged in write some doc for connection or account creation right in the console.
    @click.pass_context
    def run(ctx, *args, **kwargs):
        if get_jwt_token() is None and (ctx.command_path not in ["appollo signin", "appollo signout", "appollo signup"]):
            import textwrap

            from rich.text import Text

            console.print(Text.from_markup(
                textwrap.dedent(
                    f"""
                                    [red bold]You are not logged in. To use Appollo you need a user account.[/red bold]

                                    [code]$ appollo signup --help[/code] for instructions to create your account.

                                    [code]$ appollo signin --help[/code] for instructions to log in your account.

                                    =============================================
                                """
                )
            ))

        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(run, f)


def terminal_menu(api_route, prompt_text, key_fieldname="key", name_fieldname="name", does_not_exist_msg="No item to select."):
    """ A simple helper function to have a select terminal menu.

    Ideally this function should be integrated in a custom click.option and click.argument but it is not easy.
    """
    from simple_term_menu import TerminalMenu

    from appollo import api

    item_list = api.get(api_route)
    terminal_ready_list = ["%s (%s)" % (item[name_fieldname], item[key_fieldname]) for item in item_list]
    if len(terminal_ready_list) == 0:
        console.print(does_not_exist_msg)
        return
    elif len(terminal_ready_list) == 1:
        value = item_list[0][key_fieldname]
    else:
        console.print("%s : " % prompt_text)
        terminal_menu = TerminalMenu(terminal_ready_list)
        menu_entry_index = terminal_menu.show()
        value = item_list[menu_entry_index][key_fieldname]

    return value
