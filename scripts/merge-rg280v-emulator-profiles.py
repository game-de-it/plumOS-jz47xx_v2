#!/usr/bin/env python3
"""Update supported launcher profiles without replacing user system settings."""

import json
import sys
from pathlib import Path


installed_path, defaults_path, output_path = map(Path, sys.argv[1:])
installed = json.loads(installed_path.read_text())
defaults = json.loads(defaults_path.read_text())
supported = {"nes", "gb", "gbc", "sfc", "gba", "megadrive"}
profiles = {system["id"]: system for system in defaults["systems"] if system["id"] in supported}
for system in installed["systems"]:
    if system.get("id") in profiles:
        source = profiles[system["id"]]
        system["launch_profiles"] = source["launch_profiles"]
        system["default_launch_profile"] = source["default_launch_profile"]
output_path.write_text(json.dumps(installed, ensure_ascii=False, indent=2) + "\n")
