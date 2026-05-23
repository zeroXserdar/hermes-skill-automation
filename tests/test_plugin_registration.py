from pathlib import Path

from hermes_cli.plugins import PluginContext, PluginManager, PluginManifest

from plugin.skill_factory_v1 import register


class DummyCtx(PluginContext):
    def __init__(self, base_dir: Path):
        manager = PluginManager()
        manifest = PluginManifest(
            name="skill_factory_v1",
            version="0.1.0",
            description="description",
            author="Hermes Agent",
            source="user",
            path=str(base_dir),
            kind="standalone",
            key="skill_factory_v1",
        )
        super().__init__(manifest, manager)


def test_registers_commands_hooks_cli_and_skill(tmp_path: Path):
    ctx = DummyCtx(tmp_path)
    register(ctx)

    plugin_commands = ctx._manager._plugin_commands
    hook_names = set(ctx._manager._hooks.keys())
    cli_names = set(ctx._manager._cli_commands.keys())
    skills = ctx._manager._plugin_skills

    assert {"skillfactory-status", "skillfactory-last", "skillfactory-export", "skillfactory-propose"} <= set(plugin_commands.keys())
    assert {"pre_tool_call", "post_tool_call", "on_session_finalize", "on_session_reset"} <= hook_names
    assert "skill-factory-v1" in cli_names
    assert "skill_factory_v1:workflow-to-skill" in skills
    assert skills["skill_factory_v1:workflow-to-skill"]["bare_name"] == "workflow-to-skill"
