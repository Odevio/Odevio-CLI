import os
from configparser import ConfigParser

import click
from rich.console import Console

APP_NAME = "Odevio"
API_BASE_URL = "https://odevio.com"


console = Console()


def get_config_path():
    """ :return Odevio's config file path """
    return os.path.join(click.get_app_dir(APP_NAME), 'config.ini')


def read_config():
    """ Reads the config.ini file.

    :return a dict of the configuration
    """
    config_file = get_config_path()
    parser = ConfigParser()
    parser.read(config_file)

    return {
        "JWT_TOKEN": parser.has_section("auth") and parser.has_option("auth", "JWT_TOKEN") and parser.get("auth", "JWT_TOKEN") or None
    }


def write_jwt_token(token):
    """ Writes the JWT token to the config.ini file.

    creates the folder where the config lies and the config.ini file if necessary.
    """
    config_directory = click.get_app_dir(APP_NAME)
    config_file = os.path.join(config_directory, 'config.ini')
    parser = ConfigParser()
    parser.read(config_file)

    if not parser.has_section("auth"):
        parser.add_section("auth")
    parser.set("auth", "JWT_TOKEN", token)

    if not os.path.exists(config_directory):
        os.makedirs(config_directory)
        console.print(f"Created a configuration file for Odevio : {config_file}")

    with open(config_file, 'w') as f:
        parser.write(f)


def delete_jwt_token():
    """ Deletes the JWT token from the config.ini file."""
    config_directory = click.get_app_dir(APP_NAME)
    config_file = os.path.join(config_directory, 'config.ini')
    parser = ConfigParser()
    parser.read(config_file)

    if parser.has_section("auth") and parser.has_option("auth", "jwt_token"):
        parser.remove_option("auth", "jwt_token")

        with open(config_file, 'w') as f:
            parser.write(f)


def get_jwt_token():
    """ Returns the JWT token or None. """
    config = read_config()
    return config.get('JWT_TOKEN', None)
