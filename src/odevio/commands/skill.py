import click

# Commands the skill may run without asking each time. Everything here either only reads, or writes
# something that can be written again differently - never something that cannot be taken back.
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


STAMP_FILE = ".installed-version"

# The skill name, and where Claude Code - the turn-key target - looks for skills and keeps its
# settings. Other agents that support the open Agent Skills standard read the same skill files from
# their own directory; install into it with ``--to``.
SKILL_NAME = "odevio"
CLAUDE_SKILLS_DIR = (".claude", "skills")
CLAUDE_SETTINGS_FILE = (".claude", "settings.json")

# Agents that read the open Agent Skills standard, and where each keeps its skills - the same relative
# path under the home directory (machine-wide) or a project root (with --project). Only Claude Code also
# gets its commands pre-approved; the others place the same skill and apply their own approval rules.
# Any agent not listed here is still reachable with --to <its skills directory>.
AGENTS = {
    "claude-code": {
        "label": "Claude Code",
        "skills_dir": CLAUDE_SKILLS_DIR,
        "permissions": True,
        "invoke": "It is set up for Claude Code, the default, and available as [code]/odevio[/code] in {scope}.",
        "note": None,
    },
    "codex": {
        "label": "Codex CLI",
        "skills_dir": (".codex", "skills"),
        "permissions": False,
        "invoke": "It is now available to Codex CLI in {scope}.",
        "note": None,
    },
    "gemini": {
        "label": "Gemini CLI",
        "skills_dir": (".gemini", "skills"),
        "permissions": False,
        "invoke": "It is now available to Gemini CLI in {scope}.",
        "note": None,
    },
    "cursor": {
        "label": "Cursor",
        "skills_dir": (".cursor", "skills"),
        "permissions": False,
        "invoke": "It is now available to Cursor in {scope}.",
        "note": "Cursor loads project skills most reliably; if a machine-wide install is not picked up, "
                "run it again with --project inside your repository.",
    },
    # A shared convention adopted by some agents, not a guaranteed path in the standard. Installing here
    # in addition to AGENTS.md gives the widest reach; agents that do not read it are unaffected.
    "universal": {
        "label": "Agent Standard",
        "skills_dir": (".agents", "skills"),
        "permissions": False,
        "invoke": "It is now available under .agents/skills in {scope}.",
        "note": "This is a shared convention, not guaranteed for every agent. An AGENTS.md pointing at "
                "the skill is the portable fallback.",
    },
}


def installed_version():
    """ The version of Odevio currently running. """
    try:
        from importlib import metadata
    except ImportError:  # Python < 3.8
        import importlib_metadata as metadata
    return metadata.version("odevio")


def skill_source():
    """ The skill shipped inside this installation of Odevio. """
    import os

    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skill")


def refresh_copied_skill():
    """ Bring a copied skill back in step with the Odevio that was just upgraded.

    A linked skill follows the upgrade by itself. A copied one does not: it keeps answering with last
    month's instructions, and nothing the assistant does says so. Since Odevio updates itself in the
    background, there is no moment when the user would think to reinstall - so it is done for them.

    Returns the version copied, or None when there was nothing to do.
    """
    import os
    import shutil

    destination = os.path.join(os.path.expanduser("~"), *CLAUDE_SKILLS_DIR, SKILL_NAME)
    if os.path.islink(destination) or not os.path.isdir(destination):
        return None

    current = installed_version()
    stamp = os.path.join(destination, STAMP_FILE)
    try:
        with open(stamp, encoding="utf-8") as handle:
            if handle.read().strip() == current:
                return None
    except OSError:
        pass  # No stamp: installed before stamping existed, so it is certainly behind.

    shutil.rmtree(destination)
    shutil.copytree(skill_source(), destination)
    with open(stamp, "w", encoding="utf-8") as handle:
        handle.write(f"{current}\n")
    return current


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


def _install_for_agent(agent_name, base, scope, source, *, copy_files, project, force,
                        no_permissions, single):
    """ Place the skill for one agent under ``base`` and pre-approve its commands where that applies.

    Shared by a single ``--agent`` install and each step of ``--agent all``; ``single`` is False during
    a fan-out so per-agent hints that only make sense on their own are left out.
    """
    import os
    import shutil

    from odevio.settings import console

    profile = AGENTS[agent_name]
    destination = os.path.join(base, *profile["skills_dir"], SKILL_NAME)

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

    # Linking is the default because the alternative fails silently: a copy keeps working after
    # "pip install --upgrade odevio" while holding last month's instructions, and nothing about the
    # assistant's behaviour says so. A broken link is at least visible. Inside a project the skill is
    # meant to be committed and read on other machines, so there a copy is the only thing that works.
    as_copy = copy_files or project
    if as_copy:
        shutil.copytree(source, destination)
        # Stamped so a later run of the CLI can notice the copy has fallen behind and say so.
        with open(os.path.join(destination, ".installed-version"), "w", encoding="utf-8") as handle:
            handle.write(f"{installed_version()}\n")
    else:
        os.symlink(source, destination)

    console.print(f"Odevio skill installed in {destination}")
    console.print(profile["invoke"].format(scope=scope))
    if profile["note"]:
        console.print(profile["note"])
    if single and agent_name == "claude-code":
        console.print("Using another agent? Run it again with --agent codex, --agent cursor, "
                      "--agent gemini or --agent universal - or --agent all for every one.")

    # Pre-approving commands writes Claude Code's own settings.json allow rules, so it only applies to
    # Claude Code. Other agents place the same skill and apply their own approval rules.
    if not profile["permissions"]:
        console.print(f"{profile['label']} applies its own approval rules, so Odevio does not pre-approve "
                      "its commands here.")
        return

    if no_permissions:
        console.print("Its commands were not pre-approved, so each one will ask for approval.")
        return

    settings_path = os.path.join(base, *CLAUDE_SETTINGS_FILE)
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


@click.group()
def skill():
    """ Install the Odevio skill for AI agents.

    \f
    The skill teaches an AI agent such as Claude Code how to take a Flutter project all the way to an
    iPhone through Odevio: Apple setup, remote iOS build, automatic fixing of build failures, and
    delivery to TestFlight.

    Usage:
    """


@skill.command()
@click.option('--project', is_flag=True,
              help="Install for a single project instead of the whole machine. Use this to commit the skill with a repository.")
@click.option('--directory', type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
              help="With --project, the project to install into. Defaults to the current directory.")
@click.option('--copy', 'copy_files', is_flag=True,
              help="Copy the skill instead of linking it. It then stays as it is until you install again.")
@click.option('--link', is_flag=True, hidden=True,
              help="Kept for existing scripts; linking is now what happens by default.")
@click.option('--force', is_flag=True, help="Replace an existing installation.")
@click.option('--no-permissions', is_flag=True,
              help="Do not pre-approve the skill's commands. Every one of them will then ask for approval.")
@click.option('--agent', type=click.Choice(sorted(AGENTS) + ["all"]), default='claude-code',
              show_default=True,
              help="Which AI agent to install for. Claude Code also gets its commands pre-approved; the "
                   "others place the same skill and follow their own approval rules. Use 'all' to install "
                   "for every supported agent at once.")
@click.option('--to', 'to_dir', type=click.Path(resolve_path=True, file_okay=False, dir_okay=True),
              help="Install into an explicit skills directory, for any Agent Skills-compatible agent not "
                   "covered by --agent. Copies the standard files there; auto-approval is skipped.")
def install(project, directory, copy_files, link, force, no_permissions, agent, to_dir):
    """ Install the Odevio skill.

    \f
    By default the skill is installed for the whole machine, in :code:`~/.claude/skills/odevio/`, and
    becomes available as :code:`/odevio` in every project. That path is where Claude Code looks, so this
    command configures Claude Code specifically. The skill itself follows the open Agent Skills standard, so
    other agents read the same files: pass :code:`--agent codex`, :code:`--agent cursor`,
    :code:`--agent gemini` or :code:`--agent universal` to install into theirs (only Claude Code also gets
    its commands pre-approved), or :code:`--agent all` to install for every one at once. For an agent not
    listed, :code:`--to <its skills directory>` places the files anywhere. Pass :code:`--project` to install
    inside one project's skills folder instead, to commit it with the repository.

    The skill is linked rather than copied, so upgrading Odevio upgrades the skill with it. This is the
    default because the alternative fails quietly: a copy goes on answering with the instructions it was
    installed with, and nothing about the assistant's behaviour reveals that it is out of date. A broken
    link, by contrast, is obvious at once.

    :code:`--copy` takes a copy instead, which survives the Python environment being moved or removed.
    A copy left behind by an upgrade is refreshed automatically the next time Odevio updates itself, so
    it does not silently rot either. :code:`--project` always copies, since a link would be meaningless
    to anyone else who clones the repository.

    The command also adds allow rules for the skill's commands to the matching
    :code:`settings.json`, unless :code:`--no-permissions` is given. Without them the assistant asks
    for approval before nearly every command: a skill's own :code:`allowed-tools` only covers the one
    turn that invokes it, and the grant is gone as soon as you reply, so a conversation that waits for
    a build or a decision loses it immediately. Four commands are left out on purpose and always ask -
    starting a build, sending screenshots to Apple, opening a submission, and sending an app for review.

    Existing rules and settings are kept: the allow list is only ever added to, so running this again
    is harmless.

    The command is non-interactive so it can be used in a script. An existing installation is left
    untouched unless :code:`--force` is given.
    """
    import os
    import shutil

    from odevio.settings import console

    source = skill_source()
    if not os.path.isdir(source):
        raise click.ClickException(
            "The skill files are missing from this Odevio installation. Reinstall with 'pip install --upgrade odevio'."
        )

    # --to installs the standard skill files into any Agent Skills-compatible agent's directory. The
    # skill content is the same everywhere; only Claude Code's auto-approval of commands is specific, so
    # it is skipped here and the agent applies its own permission rules.
    if to_dir:
        if project or directory:
            raise click.ClickException(
                "--to installs for another agent and cannot be combined with --project or --directory."
            )
        if agent == "all":
            raise click.ClickException(
                "--to installs into one explicit directory and cannot be combined with --agent all."
            )
        destination = os.path.join(to_dir, SKILL_NAME)
        if (os.path.exists(destination) or os.path.islink(destination)) and not force:
            console.print(f"The skill is already installed in {destination}")
            console.print("Run the command again with --force to replace it.")
            return
        if os.path.islink(destination):
            os.unlink(destination)
        elif os.path.exists(destination):
            shutil.rmtree(destination)
        os.makedirs(to_dir, exist_ok=True)
        shutil.copytree(source, destination)
        with open(os.path.join(destination, STAMP_FILE), "w", encoding="utf-8") as handle:
            handle.write(f"{installed_version()}\n")
        console.print(f"Odevio skill installed in {destination}")
        console.print("It is ready for any agent that supports the open Agent Skills standard.")
        console.print("Auto-approval of the skill's commands is Claude Code-only, so this agent will ask "
                      "before each command, following its own rules.")
        return

    # Resolve where to install once; when installing for several agents they all share this base.
    if project:
        base = directory or os.getcwd()
        scope = "this project"
    else:
        if directory:
            raise click.ClickException("--directory only applies together with --project.")
        base = os.path.expanduser("~")
        scope = "every project on this machine"

    # 'all' fans out over every known agent; a single --agent installs for just that one.
    agents_to_install = list(AGENTS) if agent == "all" else [agent]
    for index, agent_name in enumerate(agents_to_install):
        if index:
            console.print("")
        _install_for_agent(
            agent_name, base, scope, source,
            copy_files=copy_files, project=project, force=force,
            no_permissions=no_permissions, single=(agent != "all"),
        )
