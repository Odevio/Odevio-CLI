import os
from functools import update_wrapper

import click
import paramiko
import sys
import threading

from appollo.settings import console, get_jwt_token


def zip_directory(directory_path):
    """ Archives a directory in a zip file and returns its name."""
    return make_zip(os.path.join(os.getcwd(), '.app'), directory_path, ["build", ".dart_tool", ".pub-cache", ".pub", ".git", ".gradle"], ["source.zip", ".app.zip", "appollo.patch"])



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


def terminal_menu(api_route, prompt_text, api_params=None, key_fieldname="key", name=lambda a: f"{a['name']} ({a['key']})", does_not_exist_msg="No item to select.", extra_options=[]):
    """ A simple helper function to have a select terminal menu.

    Ideally this function should be integrated in a custom click.option and click.argument but it is not easy.
    """
    import questionary
    from questionary import Choice

    from appollo import api

    if api_params:
        item_list = api.get(api_route, params=api_params)
    else:
        item_list = api.get(api_route)
    item_list.extend(extra_options)
    terminal_ready_list = [Choice(name(item), i) for i, item in enumerate(item_list)]
    if len(terminal_ready_list) == 0:
        console.print(does_not_exist_msg)
        return
    elif len(terminal_ready_list) == 1:
        value = item_list[0][key_fieldname]
    else:
        menu_entry_index = questionary.select(
            prompt_text,
            choices=terminal_ready_list,
            qmark="",
        ).ask()
        if menu_entry_index is None:  # When ctrl-C, exit
            exit()

        value = item_list[menu_entry_index][key_fieldname]

    return value


### Copied from shutil to add directory exlusion
def _make_zipfile(base_name, base_dir, exclude_dir=None, exclude_files=None, verbose=0, dry_run=0, logger=None):
    """Create a zip file from all the files under 'base_dir'.

    The output zip file will be named 'base_name' + ".zip".  Returns the
    name of the output zip file.
    """
    import zipfile  # late import for breaking circular dependency

    zip_filename = base_name + ".zip"
    archive_dir = os.path.dirname(base_name)

    if archive_dir and not os.path.exists(archive_dir):
        if logger is not None:
            logger.info("creating %s", archive_dir)
        if not dry_run:
            os.makedirs(archive_dir)

    if logger is not None:
        logger.info("creating '%s' and adding '%s' to it",
                    zip_filename, base_dir)

    if not dry_run:
        with zipfile.ZipFile(zip_filename, "w",
                             compression=zipfile.ZIP_DEFLATED) as zf:
            path = os.path.normpath(base_dir)
            if path != os.curdir:
                zf.write(path, path)
                if logger is not None:
                    logger.info("adding '%s'", path)
            for dirpath, dirnames, filenames in os.walk(base_dir, topdown=True):
                if exclude_dir is not None:
                    dirnames[:] = [d for d in dirnames if d not in exclude_dir]
                for name in sorted(dirnames):
                    path = os.path.normpath(os.path.join(dirpath, name))
                    zf.write(path, path)
                    if logger is not None:
                        logger.info("adding '%s'", path)
                for name in filenames:
                    if exclude_files is not None and name in exclude_files:
                        continue
                    path = os.path.normpath(os.path.join(dirpath, name))
                    if os.path.isfile(path):
                        zf.write(path, path)
                        if logger is not None:
                            logger.info("adding '%s'", path)

    return zip_filename


def make_zip(base_name, root_dir=None, exclude_dir=None, exclude_files=None, base_dir=None, verbose=0,
                 dry_run=0, logger=None):
    """Create a zip archive file

    'base_name' is the name of the file to create, minus any format-specific
    extension.

    'root_dir' is a directory that will be the root directory of the
    archive; ie. we typically chdir into 'root_dir' before creating the
    archive.  'base_dir' is the directory where we start archiving from;
    ie. 'base_dir' will be the common prefix of all files and
    directories in the archive.  'root_dir' and 'base_dir' both default
    to the current directory.  Returns the name of the archive file.
    """
    save_cwd = os.getcwd()
    if root_dir is not None:
        if logger is not None:
            logger.debug("changing into '%s'", root_dir)
        base_name = os.path.abspath(base_name)
        if not dry_run:
            os.chdir(root_dir)

    if base_dir is None:
        base_dir = os.curdir

    kwargs = {'dry_run': dry_run, 'logger': logger}

    try:
        filename = _make_zipfile(base_name, base_dir, exclude_dir, exclude_files, **kwargs)
    finally:
        if root_dir is not None:
            if logger is not None:
                logger.debug("changing back to '%s'", save_cwd)
            os.chdir(save_cwd)

    return filename


def tunnel_handler(chan, host, port):
    import socket
    import select
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        return
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()


def ssh_tunnel(host, port, username, password, remote_port, forward_host, forward_port):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port, username, password)
    except Exception as e:
        print("Failed to connect to remote host: " + str(e))
        sys.exit(1)
    print("Forwarding remote port " + str(remote_port) + " to port " + str(
        forward_port) + " on " + forward_host + ". Press ctrl+C to close the tunnel.")
    try:
        transport = client.get_transport()
        transport.request_port_forward("", remote_port)
        while True:
            chan = transport.accept(1000)
            if chan is None:
                continue
            thr = threading.Thread(target=tunnel_handler, args=(chan, forward_host, forward_port))
            thr.setDaemon(True)
            thr.start()
    except KeyboardInterrupt:
        print("\nTunnel closed")
