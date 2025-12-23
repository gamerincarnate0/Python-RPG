import json
from pathlib import Path
from plugins.registry import PluginRegistry
from plugins.schemas import validate_enemy, validate_item

PLUGIN_ROOT = Path("plugins")

def load_plugins() -> PluginRegistry:
    registry = PluginRegistry()

    if not PLUGIN_ROOT.exists():
        return registry  # No plugins installed

    for category in ("enemies", "items"):
        category_path = PLUGIN_ROOT / category
        if not category_path.exists():
            continue

        for plugin_dir in category_path.iterdir():
            if not plugin_dir.is_dir():
                continue

            data_file = plugin_dir / f"{category[:-1]}.json"
            if not data_file.exists():
                continue

            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            try:
                if category == "enemies":
                    validate_enemy(data)
                    registry.register_enemy(data["id"], data)
                else:
                    validate_item(data)
                    registry.register_item(data["id"], data)
            except ValueError as e:
                print(f"[PLUGIN ERROR] {plugin_dir.name}: {e}")

    return registry