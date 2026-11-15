#!/usr/bin/env python3
"""Adapt pinned PicoArch's SDL host for RG280V; fail on upstream drift."""

import pathlib
import re
import sys

source = pathlib.Path(sys.argv[1])


def replace(name: str, old: str, new: str) -> None:
    path = source / name
    data = path.read_text()
    if data.count(old) != 1:
        raise SystemExit(f"unexpected {name} source around {old[:50]!r}")
    path.write_text(data.replace(old, new, 1))


replace("Makefile", "scaler_neon.o unzip.o", "scaler_c.o unzip.o")
replace("Makefile", "-lpng12", "-lpng16")
replace("scale.h", "#define SCREEN_WIDTH 640\n#define SCREEN_HEIGHT 480", "#define SCREEN_WIDTH 320\n#define SCREEN_HEIGHT 240")
replace("menu.c", "#define MENU_X2 1", "#define MENU_X2 0")

scaler_source = (source / "scaler_neon.c").read_text()
marker = "void scale1x_c16("
if scaler_source.count(marker) != 1:
    raise SystemExit("C scaler marker changed")
scaler_c = (
    '#include <stdint.h>\n#include <string.h>\n#include "scaler_neon.h"\n'
    + scaler_source[scaler_source.index(marker):]
)
(source / "scaler_c.c").write_text(scaler_c)
scale_path = source / "scale.c"
scale_data = scale_path.read_text()
for factor in range(1, 7):
    for depth in (16, 32):
        scale_data = scale_data.replace(f"scale{factor}x_n{depth}", f"scale{factor}x_c{depth}")
scale_path.write_text(scale_data)

video_path = source / "plat_sdl.c"
video = video_path.read_text()
pattern = r"// begin miyoo hardware scaling support.*?// end miyoo hardware scaling support"
replacement = (
    "/* RG280V uses SDL/KMSDRM's 320x240 RGB565 surface. */\n"
    "static void buffer_init(void) {}\n"
    "static void buffer_quit(void) {}\n"
    "static void buffer_scale(unsigned w, unsigned h, size_t pitch, const void *src)\n"
    "{\n\tscale(w, h, pitch, src, screen->pixels);\n}"
)
video, count = re.subn(pattern, replacement, video, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Miyoo video block changed")
old_mode = "SDL_SetVideoMode(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_BPP * 8, SDL_SWSURFACE)"
new_mode = "SDL_SetVideoMode(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_BPP * 8, SDL_HWSURFACE | SDL_DOUBLEBUF)"
if video.count(old_mode) != 1:
    raise SystemExit("SDL video mode changed")
video = video.replace(old_mode, new_mode, 1)
video_path.write_text(video)

replace("plat_linux.c", "{ SDLK_LCTRL,     IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_B },", "{ SDLK_LCTRL,     IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_A },")
replace("plat_linux.c", "{ SDLK_SPACE,     IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_A },", "{ SDLK_SPACE,     IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_X },")
replace("plat_linux.c", "{ SDLK_LSHIFT,    IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_X },", "{ SDLK_LSHIFT,    IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_Y },")
replace("plat_linux.c", "{ SDLK_LALT,      IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_Y },", "{ SDLK_LALT,      IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_B },")
replace("plat_linux.c", "{ SDLK_RCTRL,     IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_SELECT },", "{ SDLK_ESCAPE,    IN_BINDTYPE_PLAYER12, RETRO_DEVICE_ID_JOYPAD_SELECT },")
replace("plat_linux.c", "{ SDLK_ESCAPE,    IN_BINDTYPE_EMU, EACTION_MENU },", "{ SDLK_F1,        IN_BINDTYPE_EMU, EACTION_MENU },")
replace("plat_linux.c", "{ SDLK_SPACE,     PBTN_MOK },", "{ SDLK_LCTRL,     PBTN_MOK },")
replace("plat_linux.c", "{ SDLK_LCTRL,     PBTN_MBACK },", "{ SDLK_LALT,      PBTN_MBACK },")
replace("plat_linux.c", "{ SDLK_LALT,      PBTN_MA2 },", "{ SDLK_SPACE,     PBTN_MA2 },")
replace("plat_linux.c", "{ SDLK_LSHIFT,    PBTN_MA3 },", "{ SDLK_LSHIFT,    PBTN_MA3 },")
replace("plat_linux.c", "{ SDLK_ESCAPE,    PBTN_MENU },", "{ SDLK_F1,        PBTN_MENU },")
replace("plat_linux.c", "static const struct mod_keymap in_sdl_mod_keymap[] = {", "static const struct mod_keymap in_sdl_mod_keymap[] = {\n\t{ SDLK_RETURN, SDLK_F1 }, /* SELECT + START opens PicoArch menu */")

replace("main.c", "scale_size = SCALE_SIZE_NONE;", "scale_size = SCALE_SIZE_ASPECT;")
main_path = source / "main.c"
main = main_path.read_text()
tag_pattern = r"static void get_tag_name\(const char\* in_path, char\* out_tag\) \{.*?\n\}\n\nint main"
tag_replacement = (
    "static void get_tag_name(const char* in_path, char* out_tag) {\n"
    "\tconst char *system = getenv(\"PLUMOS_PICOARCH_SYSTEM\");\n"
    "\tif (system && system[0]) {\n"
    "\t\tsnprintf(out_tag, MAX_PATH, \"%s\", system);\n"
    "\t\treturn;\n\t}\n"
    "\tconst char *slash = strrchr(in_path, '/');\n"
    "\tsnprintf(out_tag, MAX_PATH, \"%s\", slash ? slash + 1 : in_path);\n"
    "}\n\nint main"
)
main, count = re.subn(tag_pattern, tag_replacement, main, count=1, flags=re.S)
if count != 1:
    raise SystemExit("tag function changed")
main_path.write_text(main)

core_path = source / "core.c"
core = core_path.read_text()
directory_pattern = r"static void set_directories\(const char \*core_name, const char \*tag_name\) \{.*?\n\}\n\n// based on eggs"
directory_replacement = (
    "static void set_directories(const char *core_name, const char *tag_name) {\n"
    "\tconst char *home = getenv(\"HOME\");\n"
    "\tconst char *save_root = getenv(\"PLUMOS_PICOARCH_SAVE_ROOT\");\n"
    "\tconst char *bios_dir = getenv(\"PLUMOS_PICOARCH_BIOS_DIR\");\n"
    "\tif (!home || !save_root || !bios_dir) PA_FATAL(\"PicoArch paths are unset\");\n"
    "\tsnprintf(config_dir, MAX_PATH, \"%s/.picoarch-%s-%s/\", home, core_name, tag_name);\n"
    "\tmkdir(config_dir, 0755);\n"
    "\tsnprintf(save_dir, MAX_PATH, \"%s/%s/\", save_root, tag_name);\n"
    "\tmkdir(save_root, 0755);\n"
    "\tmkdir(save_dir, 0755);\n"
    "\tsnprintf(system_dir, MAX_PATH, \"%s\", bios_dir);\n"
    "}\n\n// based on eggs"
)
core, count = re.subn(directory_pattern, directory_replacement, core, count=1, flags=re.S)
if count != 1:
    raise SystemExit("directory function changed")
needle = "\tif (!current_core.retro_load_game(&game_info)) {"
if core.count(needle) != 1:
    raise SystemExit("controller initialization marker changed")
core = core.replace(
    needle,
    "\tif (current_core.retro_set_controller_port_device)\n"
    "\t\tcurrent_core.retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD);\n\n"
    + needle,
    1,
)
core_path.write_text(core)
