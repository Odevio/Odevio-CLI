import click

# Commands the skill may run without asking each time. Everything here either only reads, or writes
# something that can be written again differently — never something that cannot be taken back.
#
# Deliberately absent, and to stay absent: "build start", which spends an hour of a Mac someone else
# is queued for; "screenshot push", which replaces the pictures on Apple with no copy kept;
# "app check-submittable", which opens a submission Apple does not allow to be deleted; and
# "app submit", which puts the app in front of a reviewer and freezes the page. Those four are worth
# a human saying yes to, every time.
PRE_APPROVED_COMMANDS = [
    "odevio profile",
    "odevio app ls",
    "odevio app store-status",
    "odevio app categories",
    "odevio app screenshots",
    "odevio app set-metadata",
    "odevio app attach-build",
    "odevio apple ls",
    "odevio apple detail",
    "odevio build ls",
    "odevio build detail",
    "odevio build logs",
    "odevio build ipa",
    "odevio build flutter-versions",
    "odevio privacy scan",
    "odevio screenshot devices",
    "odevio team ls",
    # The project's own toolchain, for checking the code before spending a build on it.
    "flutter pub get",
    "flutter test",
    "flutter --version",
    "dart analyze",
    "dart --version",
    # Reading history explains why a build that used to work has stopped. Read-only forms only.
    "git diff",
    "git log",
    "git show",
    "git status",
]

# Reading a command's help changes nothing, and the skill is told to check a command's options rather
# than guess them, so help is granted even for the commands that are never pre-approved themselves.
#
# These are granted as exact strings, never with a trailing wildcard. A rule like "odevio app:*" would
# read as the whole group and quietly cover "odevio app submit --confirm" along with it.
HELP_COMMANDS = [
    "odevio --help",
    "odevio app --help",
    "odevio apple --help",
    "odevio build --help",
    "odevio privacy --help",
    "odevio screenshot --help",
    "odevio skill --help",
    "odevio team --help",
    "odevio user --help",
    # The four that always ask before running. Reading what they do is not running them.
    "odevio app check-submittable --help",
    "odevio app submit --help",
    "odevio build start --help",
    "odevio screenshot push --help",
]


def permission_rules():
    """ The allow rules that let the skill work without a prompt on every command.

    Four forms per command: with and without the ``COLUMNS=200`` prefix the skill uses to stop the
    CLI wrapping its output, and with and without a trailing argument, since a rule ending in
    ``:*`` does not match a command that has nothing after it.

    Help is the exception, granted only as the exact string. A wildcard on it would widen the rule to
    whatever follows, which for a group name is every subcommand it has.
    """
    rules = []
    for command in PRE_APPROVED_COMMANDS:
        for prefix in ("", "COLUMNS=200 "):
            rules.append(f"Bash({prefix}{command})")
            rules.append(f"Bash({prefix}{command}:*)")
    for command in HELP_COMMANDS:
        for prefix in ("", "COLUMNS=200 "):
            rules.append(f"Bash({prefix}{command})")
    return rules


def write_permission_rules(settings_path):
    """ Add the rules to a Claude Code settings file, leaving everything else in it untouched.

    Returns how many were added. Existing rules are kept: this only ever grows the allow list, so
    running it again is harmless and never takes a permission away.
    """
    import json
    import os

    settings = {}
    if os.path.exists(settings_path):
        with open(settings_path, encoding="utf-8") as handle:
            content = handle.read().strip()
        if content:
            settings = json.loads(content)

    permissions = settings.setdefault("permissions", {})
    allowed = permissions.setdefault("allow", [])
    added = [rule for rule in permission_rules() if rule not in allowed]
    allowed.extend(added)

    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as handle:
        json.dump(settings, handle, indent=2)
        handle.write("\n")
    return len(added)


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
@click.option('--no-permissions', is_flag=True,
              help="Do not pre-approve the skill's commands. Every one of them will then ask for approval.")
def install(project, directory, link, force, no_permissions):
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

    The command also adds allow rules for the skill's commands to the matching
    :code:`settings.json`, unless :code:`--no-permissions` is given. Without them the assistant asks
    for approval before nearly every command: a skill's own :code:`allowed-tools` only covers the one
    turn that invokes it, and the grant is gone as soon as you reply, so a conversation that waits for
    a build or a decision loses it immediately. Three commands are left out on purpose and always ask
    — starting a build, sending screenshots to Apple, and opening a submission.

    Existing rules and settings are kept: the allow list is only ever added to, so running this again
    is harmless.

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

    if no_permissions:
        console.print("Its commands were not pre-approved, so each one will ask for approval.")
        return

    settings_path = os.path.join(base, ".claude", "settings.json")
    try:
        added = write_permission_rules(settings_path)
    except (OSError, ValueError) as error:
        # A hand-edited settings file that no longer parses should not lose the installation that
        # already succeeded, so this is reported rather than raised.
        console.print(f"[warning]Could not pre-approve its commands in {settings_path}:[/warning] {error}")
        console.print("The skill works regardless; it will just ask before each command.")
        return

    if added:
        console.print(f"Pre-approved {added} command patterns in {settings_path}, so it can read your "
                      "project and Odevio without asking each time.")
    else:
        console.print("Its commands were already pre-approved.")
    console.print("Starting a build, sending screenshots to Apple and opening a submission still ask.")
