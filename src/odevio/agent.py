""" Which AI agent, if any, drives the CLI — told to the server so it can tell agents from people. """
import os

AGENTS = {
    "claude": ("claude", "claude-code", "anthropic"),
    "codex": ("codex", "openai", "openai-codex"),
    "gemini": ("gemini", "gemini-cli", "google"),
    "grok": ("grok", "xai"),
    "cursor": ("cursor",),
    "copilot": ("copilot", "github-copilot"),
    "windsurf": ("windsurf", "codeium"),
}

_declared = None


def declare(name):
    global _declared
    _declared = name


def normalise(name):
    """ One of AGENTS' keys, or "other" for an agent this list does not know. """
    value = (name or "").strip().lower()
    for agent, aliases in AGENTS.items():
        if any(value == alias or value.startswith((alias + "-", alias + "_")) for alias in aliases):
            return agent
    return "other"


def current():
    """ The agent driving this run, normalised, or None when a person types the commands. """
    if _declared:
        return normalise(_declared)
    if os.environ.get("AI_AGENT"):
        return normalise(os.environ["AI_AGENT"])
    if os.environ.get("CLAUDECODE") == "1":
        return "claude"
    return None
