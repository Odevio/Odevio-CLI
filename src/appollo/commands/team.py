import click

from appollo.helpers import login_required_warning_decorator


@click.group('team')
def team():
    """ Subcommands to manage teams and corresponding users.

    A user can be part of multiple teams. Each team has only one admin. The admin can add or remove users based
    on their username.

    The team system is used in case a user wants to share access to his Apple Developer Account, his app identifiers or
    his builds to other developers with whom he collaborates.


    \f
    .. warning:: If an object (App or Apple Developer Account) is linked to a team then all members of this team have
                 full control over the object.

    Usage :

    """
    pass


@team.command()
@login_required_warning_decorator
def ls():
    """ Lists the teams to which the logged in user has access.

    Returns a list with :

        - General team information
        - List of team members
        - List of app identifiers in the team
        - List of Apple Developer accounts to which the team has access

    \f
    Example output :

    .. image:: /img/appollo-team-ls.png
        :alt: example output of the appollo team ls command
        :align: center

    Usage :

    """
    from rich.tree import Tree
    from rich.syntax import Syntax
    from appollo import api
    from appollo.settings import console

    teams = api.get("/teams/")

    if teams:
        tree = Tree("My teams")
        for team_instance in teams:
            t_team = tree.add(f"{team_instance.get('key')} [purple]{team_instance.get('name')}[/purple]")
            t_team.add(f"Admin username : [green]{team_instance['manager']['username']}[/green]")
            t_team.add(f"Admin email : [green]{team_instance['manager']['email']}[/green]")
            t_team_members = t_team.add('Members')
            for member_item in team_instance['members']:
                t_team_members.add(f"[green]{member_item}[/green]")
            if len(team_instance['applications']) > 0:
                t_team_apps = t_team.add('Applications')
                for team_item in team_instance['applications']:
                    t_team_apps.add(f"[green]{team_item['key']}[/green] | {team_item['name']} | "
                                    f"{team_item['bundle_id']}")
            if len(team_instance['apple_developer_accounts']) > 0:
                t_team_acc = t_team.add('Apple Developer Accounts')
                for acc_item in team_instance['apple_developer_accounts']:
                    t_team_acc.add(f"[green]{acc_item['key']}[/green] | {acc_item['name']} | {acc_item['manager']}")
        console.print(tree)
    else:
        code = Syntax(code="$ appollo team mk --name TEAM_NAME", lexer="shell")
        console.print(f"You are not part of any teams. Create one with")
        console.print(code)


@team.command()
@login_required_warning_decorator
@click.option('--name', prompt=True)
def mk(name):
    """ Creates a team and sets the logged in user as team admin. """
    from appollo import api
    from appollo.settings import console

    team_instance = api.post("/teams/", json_data={
        "name": name,
    })

    if team_instance:
        console.print(f"Created team {team_instance['name']} successfully. It has key {team_instance['key']}")


@team.command()
@login_required_warning_decorator
@click.argument('key', required=True)
@click.confirmation_option(prompt='Are you sure you want to delete the team ? \nThis action cannot be reverted.')
def rm(key):
    """ Deletes a team. """
    from appollo import api
    from appollo.settings import console

    team_instance = api.delete(f"/teams/{key}/")

    if team_instance:
        console.print(f"deleted team \"{key}\" successfully.")


@team.group("member")
def member():
    """ Commands to manage team members."""
    pass


@member.command('add')
@login_required_warning_decorator
@click.argument('key')
@click.option('--username', prompt=True, help="username of the new team member")
def add_member(key, username):
    """ Adds a user to a team. """
    from rich.tree import Tree

    from appollo import api
    from appollo.settings import console

    try:
        team_instance = api.post(f"/teams/{key}/members/{username}/")
    except api.NotFoundException:
        console.print("Team or username not found")
        return

    if team_instance:
        t_team = Tree(team_instance.get('name'))
        t_team.add(f"Admin username : [green]{team_instance['manager']['username']}[/green]")
        t_team.add(f"Admin email : [green]{team_instance['manager']['email']}[/green]")
        t_team_members = t_team.add('Members')
        for member_instance in team_instance['members']:
            t_team_members.add(f"[green]{member_instance}[/green]")
        console.print(t_team)


@member.command('rm')
@login_required_warning_decorator
@click.argument('key')
@click.option('--username', prompt=True, help="username of the team member to remove")
def rm_member(key, username):
    """ Removes a user from a team."""
    from appollo import api
    from appollo.settings import console

    deleted = api.delete(f"/teams/{key}/members/{username}/")

    if deleted:
        console.print(f"User {username} successfully removed from team {key}")
