#!/usr/bin/env python3
"""Update supported launcher profiles without replacing user system settings."""

import json
import sys
from pathlib import Path


installed_path, defaults_path, output_path = map(Path, sys.argv[1:])
installed = json.loads(installed_path.read_text())
defaults = json.loads(defaults_path.read_text())
supported = {
    "nes", "fds", "gb", "gbc", "sfc", "gba", "megadrive", "mastersystem",
    "gamegear", "sega32x", "segacd", "pcengine", "supergrafx", "pcenginecd",
    "psx", "wonderswan", "fbneo",
}
profiles = {system["id"]: system for system in defaults["systems"] if system["id"] in supported}
installed_ids = {system["id"] for system in installed["systems"]}
for system in installed["systems"]:
    if system.get("id") in profiles:
        source = profiles[system["id"]]
        system["launch_profiles"] = source["launch_profiles"]
        system["default_launch_profile"] = source["default_launch_profile"]
        if system["id"] == "fds":
            # FCEUmm currently renders incorrect colors and runs below full speed.
            system["enabled"] = False
        if system["id"] == "sega32x":
            # PicoDrive remains around 30 FPS on RG280V in the hardware test.
            system["enabled"] = False
for system in defaults["systems"]:
    if system["id"] in supported and system["id"] not in installed_ids:
        installed["systems"].append(system)
installed["systems"].sort(key=lambda system: system.get("sort_order", 9999))
output_path.write_text(json.dumps(installed, ensure_ascii=False, indent=2) + "\n")
