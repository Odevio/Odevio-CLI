#!/usr/bin/env python

import click

from odevio.commands.build import build
from odevio.commands.user import signup, signin, signout, profile
from odevio.commands.team import team
from odevio.commands.app import app
from odevio.commands.apple import apple
from odevio.helpers import check_new_version


@click.group()
@click.version_option(version='1.1.0', message="""Odevio, %(version)s
Copyright (C) 2023 Odevio‡
License : The MIT License
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.""")
def odevio():
    """ Command line tool to build & release your flutter apps easily.

    \b
    Github : https://github.com/Odevio/Odevio-CLI
    Documentation : https://odevio.readthedocs.io/en/master/
    Download : https://pypi.org/project/odevio/

    \f

    **How does it work ?**

    .. image:: /img/odevio-cli-remote-explanation.png
        :alt: image explaining the Odevio-cli and Odevio-Remote architecture
        :align: center

    The Odevio tool is composed of :

            - *Odevio-Remote* : The pre-configured build machines which handle the setup, build and release of your app
            - *Odevio-cli* : The CLI command line that works as an interface to start Odevio-Remote build machines

    This reference guide only covers the Odevio-cli features.

    .. note:: Odevio-Remotes are MacOS build machines on which the flutter build of your application is executed.

    .. |github| raw:: html

       <a href="https://github.com/Odevio/Odevio-CLI" target="_blank">https://github.com/Odevio/Odevio-CLI</a>

    .. |pypi| raw:: html

       <a href="https://pypi.org/project/odevio/" target="_blank">https://pypi.org/project/odevio/</a>

    Usage:
    """
    check_new_version()


# register the subgroups to the main CLI commands
odevio.add_command(build)
odevio.add_command(signup)
odevio.add_command(signin)
odevio.add_command(signout)
odevio.add_command(profile)
odevio.add_command(team)
odevio.add_command(app)
odevio.add_command(apple)

if __name__ == '__main__':
    odevio()
