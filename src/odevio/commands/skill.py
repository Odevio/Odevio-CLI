import click


@click.group()
def skill():
    """ Install the Odevio skill for AI coding assistants.

    \f
    The skill teaches an assistant such as Claude Code how to take a Flutter project all the way to an
    iPhone through Odevio: Apple setup, remote iOS build, automatic fixing of build failures, and
    delivery to TestFlight.

    Usage:
    """


@skill.command()
@click.option('--project', is_flag=True,
              help="Install for a single project instead of the whole machine. Use this to commit the skill with a repository.")
@click.option('--directory', type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
              help="With --project, the project to install into. Defaults to the current directory.")
@click.option('--link', is_flag=True,
              help="Symlink the skill instead of copying it, so upgrading Odevio also upgrades the skill.")
@click.option('--force', is_flag=True, help="Replace an existing installation.")
def install(project, directory, link, force):
    """ Install the Odevio skill.

    \f
    By default the skill is installed for the whole machine, in :code:`~/.claude/skills/odevio/`, and
    becomes available as :code:`/odevio` in every project. That path is where Claude Code looks, so this
    command configures Claude Code specifically. The skill itself follows the open Agent Skills standard, so
    another assistant supporting it can use the same files placed wherever it expects them. Pass :code:`--project` to install it inside one
    project's :code:`.claude/skills/` instead, which is what you want when the skill should be committed
    with the repository.

    :code:`--link` creates a symlink rather than a copy. The assistant follows it, so a later
    :code:`pip install --upgrade odevio` also upgrades the skill. A copy is more robust: it survives the
    Python environment being moved or removed.

    The command is non-interactive so it can be used in a script. An existing installation is left
    untouched unless :code:`--force` is given.
    """
    import os
    import shutil

    from odevio.settings import console

    source = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skill")
    if not os.path.isdir(source):
        raise click.ClickException(
            "The skill files are missing from this Odevio installation. Reinstall with 'pip install --upgrade odevio'."
        )

    if project:
        base = directory or os.getcwd()
        scope = "this project"
    else:
        if directory:
            raise click.ClickException("--directory only applies together with --project.")
        base = os.path.expanduser("~")
        scope = "every project on this machine"
    destination = os.path.join(base, ".claude", "skills", "odevio")

    # islink is checked separately: a broken symlink is invisible to exists() and would otherwise make the
    # copy fail with a confusing error.
    if (os.path.exists(destination) or os.path.islink(destination)) and not force:
        console.print(f"The skill is already installed in {destination}")
        console.print("Run the command again with --force to replace it.")
        return

    if os.path.islink(destination):
        os.unlink(destination)
    elif os.path.exists(destination):
        shutil.rmtree(destination)
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    if link:
        os.symlink(source, destination)
    else:
        shutil.copytree(source, destination)

    console.print(f"Odevio skill installed in {destination}")
    console.print(f"It is now available as [code]/odevio[/code] in {scope}.")
    if link:
        console.print("Linked to this Odevio installation, so upgrading Odevio upgrades the skill.")
