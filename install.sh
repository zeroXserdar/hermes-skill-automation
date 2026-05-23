#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PLUGIN_DST="$HERMES_HOME/plugins/skill_factory_v1"

mkdir -p "$HERMES_HOME/plugins"
rm -rf "$PLUGIN_DST"
mkdir -p "$PLUGIN_DST"
cp -R "$REPO_ROOT/plugin/skill_factory_v1/." "$PLUGIN_DST/"

echo "Installed skill_factory_v1 plugin to: $PLUGIN_DST"
echo "If Hermes is running, restart it so plugin discovery reloads."
echo "Plugin-bundled helper skill installed under: $PLUGIN_DST/skills/workflow-to-skill/SKILL.md"
