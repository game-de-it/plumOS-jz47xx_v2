#!/usr/bin/env python3
"""Update only the PSX launcher choices in an installed FE configuration."""

import json
import sys
from pathlib import Path


installed_path, defaults_path, output_path = map(Path, sys.argv[1:4])
installed = json.loads(installed_path.read_text())
defaults = json.loads(defaults_path.read_text())
source = next(system for system in defaults["systems"] if system["id"] == "psx")
target = next(system for system in installed["systems"] if system["id"] == "psx")
target["launch_profiles"] = source["launch_profiles"]
target["default_launch_profile"] = source["default_launch_profile"]
output_path.write_text(json.dumps(installed, ensure_ascii=False, indent=2) + "\n")
