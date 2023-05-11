#!/usr/bin/env python

import click

from appollo.commands.build import build
from appollo.commands.user import signup, signin, signout, profile
from appollo.commands.team import team
from appollo.commands.app import app
from appollo.commands.apple import apple


@click.group()
@click.version_option(version='1.1.0', message="""Appollo, %(version)s
Copyright (C) 2022 Appollo‡
License : The MIT License
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.""")
def appollo():
    """ Command line tool to build & release your flutter apps easily.

    \b
    Github : https://github.com/Appollo-CLI/Appollo
    Documentation : https://appollo.readthedocs.io/en/master/
    Download : https://pypi.org/project/appollo/

    \f

    **How does it work ?**

    .. image:: /img/appollo-cli-remote-explanation.png
        :alt: image explaining the Appollo-cli and Appollo-Remote architecture
        :align: center

    The Appollo tool is composed of :

            - *Appollo-Remote* : The pre-configured build machines which handle the setup, build and release of your app
            - *Appollo-cli* : The CLI command line that works as an interface to start Appollo-Remote build machines

    This reference guide only covers the Appollo-cli features.

    .. note:: Appollo-Remotes are MacOS build machines on which the flutter build of your application is executed.

    .. |github| raw:: html

       <a href="https://github.com/Appollo-CLI/Appollo" target="_blank">https://github.com/Appollo-CLI/Appollo</a>

    .. |pypi| raw:: html

       <a href="https://pypi.org/project/appollo/" target="_blank">https://pypi.org/project/appollo/</a>

    Usage:
    """
    pass


# register the subgroups to the main CLI commands
appollo.add_command(build)
appollo.add_command(signup)
appollo.add_command(signin)
appollo.add_command(signout)
appollo.add_command(profile)
appollo.add_command(team)
appollo.add_command(app)
appollo.add_command(apple)

if __name__ == '__main__':
    appollo()
