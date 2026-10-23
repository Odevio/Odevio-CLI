""" The hidden --agent option and the agent name sent to the server. Needs no server: python -m tests.agent_test """
import os

import click
from click.testing import CliRunner

from odevio import agent
from odevio.__main__ import odevio


def _commands(command):
    yield command
    if isinstance(command, click.Group):
        for sub in command.commands.values():
            yield from _commands(sub)


def test_every_command_takes_one_agent_option():
    for command in _commands(odevio):
        names = [p for p in command.params if "--agent" in getattr(p, "opts", ())]
        assert len(names) == 1, f"{command.name}: {len(names)} --agent options"


def test_the_option_is_read_after_variadic_arguments():
    from unittest import mock

    from odevio import api

    agent.declare(None)
    with mock.patch.object(api, "_request", return_value=False):
        result = CliRunner().invoke(odevio, ["screenshot", "listing", "preview", "ABC", "1", "2", "--agent", "gemini"])
    assert "No such option" not in result.output, result.output
    assert agent.current() == "gemini"
    agent.declare(None)


def test_a_group_and_the_root_accept_it():
    for args in (["screenshot", "--agent", "claude"], ["--version", "--agent", "claude"]):
        result = CliRunner().invoke(odevio, args)
        assert "No such option" not in result.output, (args, result.output)


def test_skill_install_keeps_its_own_agent_option():
    install = odevio.commands["skill"].commands["install"]
    option = next(p for p in install.params if "--agent" in p.opts)
    assert isinstance(option.type, click.Choice), "skill install --agent must stay the install target"


def test_names_are_normalised():
    cases = {"claude": "claude", "Claude-Code": "claude", "claude-code_2-1-308_agent": "claude",
             "gemini-cli": "gemini", "xai": "grok", "github-copilot": "copilot", "homemade": "other"}
    for value, expected in cases.items():
        assert agent.normalise(value) == expected, (value, agent.normalise(value))


def test_the_environment_is_the_fallback():
    saved = {k: os.environ.pop(k, None) for k in ("AI_AGENT", "CLAUDECODE")}
    try:
        agent.declare(None)
        assert agent.current() is None
        os.environ["AI_AGENT"] = "codex"
        assert agent.current() == "codex"
        agent.declare("grok")
        assert agent.current() == "grok"
    finally:
        agent.declare(None)
        os.environ.pop("AI_AGENT", None)
        os.environ.update({k: v for k, v in saved.items() if v is not None})


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print(name, "OK")
