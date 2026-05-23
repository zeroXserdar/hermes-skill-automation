from pathlib import Path

from plugin.skill_factory_v1 import register


class DummyCtx:
    def __init__(self):
        self.skills = []
        self.hooks = []
        self.commands = []
        self.cli_commands = []

    def register_skill(self, **kwargs):
        self.skills.append(kwargs)

    def register_hook(self, name, handler):
        self.hooks.append((name, handler))

    def register_command(self, **kwargs):
        self.commands.append(kwargs)

    def register_cli_command(self, **kwargs):
        self.cli_commands.append(kwargs)


def test_register_wires_expected_surfaces(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "home"))
    ctx = DummyCtx()
    register(ctx)

    command_names = {entry["name"] for entry in ctx.commands}
    assert "skillfactory-status" in command_names
    assert "skillfactory-export" in command_names
    assert "skillfactory-propose" in command_names
    assert any(item[0] == "pre_tool_call" for item in ctx.hooks)
    assert any(item[0] == "on_session_finalize" for item in ctx.hooks)
    assert any(cmd["name"] == "skill-factory-v1" for cmd in ctx.cli_commands)
    assert any(skill["name"] == "workflow-to-skill" for skill in ctx.skills)
