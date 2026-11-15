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
if video.count("#include <math.h>") != 1:
    raise SystemExit("SDL includes changed")
video = video.replace("#include <math.h>", "#include <math.h>\n#include <stdint.h>\n#include <stdlib.h>", 1)
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
conversion = '''static uint16_t *converted_frame;
static size_t converted_frame_pixels;

static const void *prepare_rgb565_frame(const void *data, unsigned width,
                                        unsigned height, size_t pitch,
                                        size_t *output_pitch)
{
    size_t pixel_count;
    unsigned y;
    if (!data || !width || !height || !output_pitch)
        return NULL;
    if (core_pixel_format == RETRO_PIXEL_FORMAT_RGB565) {
        *output_pitch = pitch;
        return data;
    }
    pixel_count = (size_t)width * height;
    if (pixel_count > converted_frame_pixels) {
        uint16_t *next = realloc(converted_frame, pixel_count * sizeof(*next));
        if (!next) return NULL;
        converted_frame = next;
        converted_frame_pixels = pixel_count;
    }
    for (y = 0; y < height; y++) {
        uint16_t *dst = converted_frame + (size_t)y * width;
        unsigned x;
        if (core_pixel_format == RETRO_PIXEL_FORMAT_XRGB8888) {
            const uint32_t *src = (const uint32_t *)((const uint8_t *)data + (size_t)y * pitch);
            for (x = 0; x < width; x++) {
                uint32_t pixel = src[x];
                dst[x] = (uint16_t)(((pixel & 0x00f80000) >> 8) |
                                  ((pixel & 0x0000fc00) >> 5) |
                                  ((pixel & 0x000000f8) >> 3));
            }
        } else {
            const uint16_t *src = (const uint16_t *)((const uint8_t *)data + (size_t)y * pitch);
            for (x = 0; x < width; x++) {
                uint16_t pixel = src[x];
                uint16_t green = (pixel >> 5) & 0x1f;
                dst[x] = (uint16_t)(((pixel & 0x7c00) << 1) |
                                  (((green << 1) | (green >> 4)) << 5) |
                                  (pixel & 0x001f));
            }
        }
    }
    *output_pitch = (size_t)width * sizeof(*converted_frame);
    return converted_frame;
}
'''
if video.count('static const void* framebuffer; // NOTE: we don\'t own this') != 1:
    raise SystemExit("framebuffer marker changed")
video = video.replace(
    "static const void* framebuffer; // NOTE: we don't own this",
    "static const void* framebuffer; // NOTE: we don't own this\n" + conversion,
    1,
)
if video.count("\tframebuffer = data;") != 1:
    raise SystemExit("video conversion marker changed")
video = video.replace(
    "\tframebuffer = data;",
    "\tconst void *rgb565 = prepare_rgb565_frame(data, width, height, pitch, &pitch);\n"
    "\tif (!rgb565) return;\n\tframebuffer = rgb565;",
    1,
)
video = video.replace("scale(width, height, pitch, data, screen->pixels);",
                      "scale(width, height, pitch, rgb565, screen->pixels);", 1)
video = video.replace("buffer_scale(width, height, pitch, data);",
                      "buffer_scale(width, height, pitch, rgb565);", 1)
video = video.replace("\tSDL_FreeSurface(screen);\n", "\tSDL_FreeSurface(screen);\n"
                      "\tfree(converted_frame);\n\tconverted_frame = NULL;\n"
                      "\tconverted_frame_pixels = 0;\n", 1)
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
if core.count("int resume_slot = -1;") != 1:
    raise SystemExit("pixel format state marker changed")
core = core.replace("int resume_slot = -1;", "int resume_slot = -1;\n"
                    "enum retro_pixel_format core_pixel_format = RETRO_PIXEL_FORMAT_0RGB1555;", 1)
perf_support = '''/* Libretro cores such as Lutro use this clock for their game timers. */
static retro_time_t pa_perf_time_usec(void) {
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) return 0;
    return (retro_time_t)now.tv_sec * 1000000 + now.tv_nsec / 1000;
}

static retro_perf_tick_t pa_perf_counter(void) {
    return (retro_perf_tick_t)pa_perf_time_usec();
}

static uint64_t pa_cpu_features(void) { return 0; }
static void pa_perf_register(struct retro_perf_counter *counter) {
    if (counter) counter->registered = true;
}
static void pa_perf_start(struct retro_perf_counter *counter) {
    if (counter) counter->start = pa_perf_counter();
}
static void pa_perf_stop(struct retro_perf_counter *counter) {
    if (counter) {
        counter->total += pa_perf_counter() - counter->start;
        counter->call_cnt++;
    }
}
static void pa_perf_log(void) {}

'''
perf_marker = "static bool pa_environment(unsigned cmd, void *data) {"
if core.count(perf_marker) != 1:
    raise SystemExit("environment marker changed")
core = core.replace(perf_marker, perf_support + perf_marker, 1)
perf_case_marker = "\tcase RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY: { /* 31 */"
perf_case = '''\tcase RETRO_ENVIRONMENT_GET_PERF_INTERFACE: { /* 28 */
        struct retro_perf_callback *cb = (struct retro_perf_callback *)data;
        if (!cb) return false;
        cb->get_time_usec = pa_perf_time_usec;
        cb->get_cpu_features = pa_cpu_features;
        cb->get_perf_counter = pa_perf_counter;
        cb->perf_register = pa_perf_register;
        cb->perf_start = pa_perf_start;
        cb->perf_stop = pa_perf_stop;
        cb->perf_log = pa_perf_log;
        break;
    }
'''
if core.count(perf_case_marker) != 1:
    raise SystemExit("performance interface insertion marker changed")
core = core.replace(perf_case_marker, perf_case + perf_case_marker, 1)
core = core.replace("#include <unistd.h>", "#include <unistd.h>\n#include <time.h>", 1)
pixel_check = """\t\tif (*format != RETRO_PIXEL_FORMAT_RGB565) {
\t\t\t/* 565 is only supported format */
\t\t\treturn false;
\t\t}"""
pixel_accept = """\t\tif (!format) return false;
\t\tswitch (*format) {
\t\tcase RETRO_PIXEL_FORMAT_0RGB1555:
\t\tcase RETRO_PIXEL_FORMAT_XRGB8888:
\t\tcase RETRO_PIXEL_FORMAT_RGB565:
\t\t\tcore_pixel_format = *format;
\t\t\tbreak;
\t\tdefault:
\t\t\treturn false;
\t\t}"""
if core.count(pixel_check) != 1:
    raise SystemExit("pixel format environment marker changed")
core = core.replace(pixel_check, pixel_accept, 1)
if core.count("\tset_environment(pa_environment);") != 1:
    raise SystemExit("core initialization marker changed")
core = core.replace("\tset_environment(pa_environment);",
                    "\tcore_pixel_format = RETRO_PIXEL_FORMAT_0RGB1555;\n"
                    "\tset_environment(pa_environment);", 1)
core = core.replace("options_init(*(const struct retro_core_option_definition **)data);",
                    "options_init((const struct retro_core_option_definition *)data);", 1)
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
replace("core.h", "extern int resume_slot;", "extern int resume_slot;\nextern enum retro_pixel_format core_pixel_format;")
