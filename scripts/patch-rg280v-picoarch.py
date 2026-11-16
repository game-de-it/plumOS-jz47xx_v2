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
replace("libpicofe/menu.c", "text_out16(x, y, name);",
        'text_out16(x, y, "%s", name);')
replace("libpicofe/menu.c",
        "text_out16(5, g_menuscreen_h - me_mfont_h - 4, menu_error_msg);",
        'text_out16(5, g_menuscreen_h - me_mfont_h - 4, "%s", menu_error_msg);')
# The upstream PicoArch overrides enable audio-driven frameskip by default.
# On RG280V this can suppress nearly every Snes9x 2005 video frame while
# emulation and audio continue at normal speed. Keep the cores' disabled
# defaults, as the 2005 Plus override already does.
replace("overrides/snes9x2005.h", '.default_value = "auto"\n',
        '.default_value = "disabled"\n')
replace("overrides/snes9x2002.h", '.default_value = "auto",\n',
        '.default_value = "disabled",\n')

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
nearest_pattern = r"static void scaleNN\(unsigned w, unsigned h, size_t pitch, const void \*src, void \*dst\) \{.*?\n\}\nstatic void scaleNN_scanline"
nearest_replacement = '''static void scaleNN(unsigned w, unsigned h, size_t pitch, const void *src, void *dst) {
    uint16_t row[SCREEN_WIDTH];
    const uint8_t *src_bytes = (const uint8_t *)src;
    uint8_t *dst_bytes = (uint8_t *)dst + dst_offs;
    unsigned previous_src_y = h;
    if (!dst_w || !dst_h || dst_w > SCREEN_WIDTH || dst_h > SCREEN_HEIGHT) return;
    for (unsigned y = 0; y < dst_h; y++) {
        unsigned src_y = (unsigned)(((uint64_t)y * h) / dst_h);
        if (src_y != previous_src_y) {
            const uint16_t *src_row = (const uint16_t *)(src_bytes + (size_t)src_y * pitch);
            unsigned sx = 0;
            unsigned error = 0;
            for (unsigned x = 0; x < dst_w; x++) {
                row[x] = src_row[sx];
                error += w;
                while (error >= dst_w) {
                    sx++;
                    error -= dst_w;
                }
            }
            previous_src_y = src_y;
        }
        memcpy(dst_bytes + (size_t)y * SCREEN_PITCH, row,
               (size_t)dst_w * sizeof(row[0]));
    }
}
static void scaleNN_scanline'''
scale_data, count = re.subn(nearest_pattern, nearest_replacement, scale_data,
                            count=1, flags=re.S)
if count != 1:
    raise SystemExit("nearest scaler marker changed")
geometry_pattern = r"static void scale_select_scaler\(unsigned w, unsigned h, size_t pitch\) \{.*?\n\}\n\nvoid scale_update_scaler"
geometry_replacement = '''static void scale_select_scaler(unsigned w, unsigned h, size_t pitch) {
    double ratio;
    unsigned integer_scale = 0;
    scaler = scale_null;
    dst_w = dst_h = dst_offs = 0;
    if (!w || !h || !pitch) return;

    /* Libretro permits aspect_ratio=0. Do not store the fallback globally:
       a core can change its geometry after the first video frame. */
    ratio = (aspect_ratio > 0.0 && isfinite(aspect_ratio))
        ? aspect_ratio : (double)w / h;

    if (scale_size == SCALE_SIZE_FULL) {
        dst_w = SCREEN_WIDTH;
        dst_h = SCREEN_HEIGHT;
    } else if (scale_size == SCALE_SIZE_ASPECT || w > SCREEN_WIDTH || h > SCREEN_HEIGHT) {
        dst_w = (unsigned)lround(SCREEN_HEIGHT * ratio);
        dst_h = SCREEN_HEIGHT;
        if (dst_w > SCREEN_WIDTH) {
            dst_w = SCREEN_WIDTH;
            dst_h = (unsigned)lround(SCREEN_WIDTH / ratio);
        }
    } else {
        /* Native keeps square source pixels and uses only integer scaling. */
        unsigned sx = SCREEN_WIDTH / w;
        unsigned sy = SCREEN_HEIGHT / h;
        integer_scale = sx < sy ? sx : sy;
        if (!integer_scale) integer_scale = 1;
        dst_w = w * integer_scale;
        dst_h = h * integer_scale;
    }
    if (!dst_w) dst_w = 1;
    if (!dst_h) dst_h = 1;
    if (dst_w > SCREEN_WIDTH) dst_w = SCREEN_WIDTH;
    if (dst_h > SCREEN_HEIGHT) dst_h = SCREEN_HEIGHT;
    dst_offs = ((SCREEN_HEIGHT - dst_h) / 2) * SCREEN_PITCH
             + ((SCREEN_WIDTH - dst_w) / 2) * SCREEN_BPP;

    if (scale_size != SCALE_SIZE_NONE || !integer_scale) {
        scaler = optimize_text ? scaleNN_text : scaleNN;
    } else if (integer_scale == 1) {
        scaler = scale1x;
    } else if (integer_scale == 2) {
        if (scale_effect == SCALE_EFFECT_LCD) scaler = scale2x_lcd;
        else if (scale_effect == SCALE_EFFECT_SCANLINE) scaler = scale2x_scanline;
        else scaler = scale2x;
    } else if (integer_scale == 3) {
        if (scale_effect == SCALE_EFFECT_LCD) scaler = scale3x_lcd;
        else if (scale_effect == SCALE_EFFECT_DMG) scaler = scale3x_dmg;
        else if (scale_effect == SCALE_EFFECT_SCANLINE) scaler = scale3x_scanline;
        else scaler = scale3x;
    } else if (integer_scale == 6 && scale_effect == SCALE_EFFECT_DMG) {
        scaler = scale6x_dmg;
    } else {
        scaler = optimize_text ? scaleNN_text : scaleNN;
    }
}

void scale_update_scaler'''
scale_data, count = re.subn(geometry_pattern, geometry_replacement, scale_data,
                            count=1, flags=re.S)
if count != 1:
    raise SystemExit("scaler geometry marker changed")
old_frame = '''\t\tscale_select_scaler(w, h, pitch);
\t\tmemset(dst, 0, SCREEN_HEIGHT * SCREEN_PITCH);
\t\tprev.w = w; prev.h = h; prev.pitch = pitch;
\t}

\tscaler(w, h, pitch, src, dst);'''
new_frame = '''\t\tscale_select_scaler(w, h, pitch);
\t\tprev.w = w; prev.h = h; prev.pitch = pitch;
\t}

    /* KMSDRM double buffers can retain pixels from the previous mode.
       Clear only the letterbox margins on every frame. */
    if (dst_w && dst_h && (dst_w != SCREEN_WIDTH || dst_h != SCREEN_HEIGHT)) {
        unsigned left = (SCREEN_WIDTH - dst_w) / 2;
        unsigned top = (SCREEN_HEIGHT - dst_h) / 2;
        unsigned right = SCREEN_WIDTH - left - dst_w;
        uint8_t *pixels = (uint8_t *)dst;
        memset(pixels, 0, (size_t)top * SCREEN_PITCH);
        memset(pixels + (size_t)(top + dst_h) * SCREEN_PITCH, 0,
               (size_t)(SCREEN_HEIGHT - top - dst_h) * SCREEN_PITCH);
        for (unsigned y = top; y < top + dst_h; y++) {
            uint8_t *row = pixels + (size_t)y * SCREEN_PITCH;
            memset(row, 0, (size_t)left * SCREEN_BPP);
            memset(row + (size_t)(left + dst_w) * SCREEN_BPP, 0,
                   (size_t)right * SCREEN_BPP);
        }
    }
\tscaler(w, h, pitch, src, dst);'''
if scale_data.count(old_frame) != 1:
    raise SystemExit("scaler frame marker changed")
scale_data = scale_data.replace(old_frame, new_frame, 1)
scale_path.write_text(scale_data)

replace("core.c", '#include "plat.h"\n', '#include "plat.h"\n#include "scale.h"\n')
core_path = source / "core.c"
core_data = core_path.read_text()
geometry_case = '''\tcase RETRO_ENVIRONMENT_SET_GEOMETRY: {
        const struct retro_game_geometry *geometry = data;
        if (!geometry || !geometry->base_width || !geometry->base_height)
            return false;
        aspect_ratio = geometry->aspect_ratio;
        scale_update_scaler();
        break;
    }
    case RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO: {
        const struct retro_system_av_info *av = data;
        if (!av || !av->geometry.base_width || !av->geometry.base_height ||
            av->timing.fps <= 0 || av->timing.sample_rate <= 0)
            return false;
        aspect_ratio = av->geometry.aspect_ratio;
        frame_rate = av->timing.fps;
        sample_rate = av->timing.sample_rate;
        plat_reinit();
        break;
    }
'''
marker = '\tcase RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY: { /* 31 */'
if core_data.count(marker) != 1:
    raise SystemExit("Libretro geometry marker changed")
core_path.write_text(core_data.replace(marker, geometry_case + marker, 1))

video_path = source / "plat_sdl.c"
video = video_path.read_text()
if video.count("#include <math.h>") != 1:
    raise SystemExit("SDL includes changed")
video = video.replace("#include <math.h>", "#include <math.h>\n#include <stdint.h>\n#include <stdlib.h>\n#include <string.h>\n#include \"main.h\"", 1)
old_flip = "static void *fb_flip(void)\n{\n\tSDL_Flip(screen);"
new_flip = '''static int needs_rgb565_handoff_swap(void)
{
    /* The current KMSDRM RGB565 plane displays NES pixels in native order.
       Swapping these cores turns Mario's blue sky cyan after a cold boot. */
    if (!strcmp(core_name, "fceumm") || !strcmp(core_name, "nestopia") ||
        !strcmp(core_name, "quicknes"))
        return 0;
    return core_pixel_format == RETRO_PIXEL_FORMAT_XRGB8888;
}

static void swap_rgb565_words(uint16_t *pixels, int width, int height, int pitch)
{
    for (int y = 0; y < height; y++) {
        uint16_t *line = (uint16_t *)((uint8_t *)pixels + y * pitch);
        for (int x = 0; x < width; x++) {
            uint16_t pixel = line[x];
            line[x] = (uint16_t)((pixel << 8) | (pixel >> 8));
        }
    }
}

static void *fb_flip(int convert_pixels)
{
    /* Retain the proven handoff for other XRGB8888 cores. */
    if (convert_pixels && needs_rgb565_handoff_swap())
        swap_rgb565_words(screen->pixels, screen->w, screen->h, screen->pitch);
    SDL_Flip(screen);'''
if video.count(old_flip) != 1:
    raise SystemExit("SDL flip marker changed")
video = video.replace(old_flip, new_flip, 1)
menu_bg_copy = "\tmemcpy(g_menubg_src_ptr, screen->pixels, g_menubg_src_h * g_menubg_src_pp * sizeof(uint16_t));"
if video.count(menu_bg_copy) != 1:
    raise SystemExit("menu background copy marker changed")
video = video.replace(menu_bg_copy,
                      "\t/* Convert the saved game frame once for the menu's RGB565 darkener. */\n"
                      "\tif (needs_rgb565_handoff_swap())\n"
                      "\t\tswap_rgb565_words(g_menubg_src_ptr, g_menubg_src_w,\n"
                      "\t\t                      g_menubg_src_h, g_menubg_src_pp * sizeof(uint16_t));", 1)
if video.count("g_menuscreen_ptr = fb_flip();") != 2:
    raise SystemExit("menu flip markers changed")
video = video.replace("g_menuscreen_ptr = fb_flip();", "g_menuscreen_ptr = fb_flip(0);", 1)
video = video.replace("g_menuscreen_ptr = fb_flip();", "g_menuscreen_ptr = fb_flip(0);", 1)
video = video.replace("\tfb_flip();\n\tSDL_LockSurface(screen);", "\tfb_flip(0);\n\tSDL_LockSurface(screen);", 1)
video = video.replace("void plat_video_flip(void)\n{\n\tfb_flip();",
                      "void plat_video_flip(void)\n{\n"
                      "\tif (g_menubg_src_ptr && g_menubg_src_w == screen->w &&\n"
                      "\t    g_menubg_src_h == screen->h &&\n"
                      "\t    g_menubg_src_pp * sizeof(uint16_t) == screen->pitch)\n"
                      "\t{\n"
                      "\t\tmemcpy(g_menubg_src_ptr, screen->pixels,\n"
                      "\t\t       g_menubg_src_h * screen->pitch);\n"
                      "\t}\n"
                      "\tfb_flip(1);", 1)
if video.count("fb_flip();"):
    raise SystemExit("unhandled SDL flip call")
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
duplicate_support = '''/* Libretro NULL video frames repeat the previous image. SDL's double
   buffer still needs that image copied into its next back buffer. */
static uint8_t last_game_frame[SCREEN_HEIGHT * SCREEN_PITCH];
static int last_game_frame_valid;
static int fresh_game_frame;

'''
marker = "void plat_video_process(const void *data, unsigned width, unsigned height, size_t pitch) {"
if video.count(marker) != 1:
    raise SystemExit("video frame process marker changed")
video = video.replace(marker, duplicate_support + marker, 1)
marker = "\tif (msg[0]) {\n\t\tvideo_print_msg(screen->pixels, screen->h, screen->pitch / SCREEN_BPP, msg);"
if video.count(marker) != 1:
    raise SystemExit("video message marker changed")
video = video.replace(marker,
                      "\tif (screen->h == SCREEN_HEIGHT && screen->pitch == SCREEN_PITCH) {\n"
                      "\t\tmemcpy(last_game_frame, screen->pixels, sizeof(last_game_frame));\n"
                      "\t\tlast_game_frame_valid = 1;\n"
                      "\t}\n"
                      "\tfresh_game_frame = 1;\n\tif (msg[0]) {\n"
                      "\t\tvideo_print_msg(screen->pixels, screen->h, screen->pitch / SCREEN_BPP, msg);", 1)
marker = "void plat_video_flip(void)\n{\n"
if video.count(marker) != 1:
    raise SystemExit("video flip marker changed")
video = video.replace(marker, marker +
                      "\tif (!fresh_game_frame) {\n"
                      "\t\t/* PSX repeats keep the displayed front buffer; avoid a needless vblank. */\n"
                      "\t\tif (last_game_frame_valid &&\n"
                      "\t\t    (!strcmp(core_name, \"pcsx_rearmed\") ||\n"
                      "\t\t     !strcmp(core_name, \"pcsx_rearmed_unai\")))\n"
                      "\t\t\treturn;\n"
                      "\t\tif (!last_game_frame_valid) return;\n"
                      "\t\tSDL_LockSurface(screen);\n"
                      "\t\tmemcpy(screen->pixels, last_game_frame, sizeof(last_game_frame));\n"
                      "\t\tif (msg[0])\n"
                      "\t\t\tvideo_print_msg(screen->pixels, screen->h, screen->pitch / SCREEN_BPP, msg);\n"
                      "\t\tSDL_UnlockSurface(screen);\n"
                      "\t\tvideo_update_msg();\n"
                      "\t}\n"
                      "\tfresh_game_frame = 0;\n", 1)
marker = "void plat_video_close(void)\n{\n\t\n}"
if video.count(marker) != 1:
    raise SystemExit("video close marker changed")
video = video.replace(marker, "void plat_video_close(void)\n{\n\tlast_game_frame_valid = 0;\n\tfresh_game_frame = 0;\n}", 1)
video = video.replace("\tSDL_FreeSurface(screen);\n", "\tSDL_FreeSurface(screen);\n"
                      "\tfree(converted_frame);\n\tconverted_frame = NULL;\n"
                      "\tconverted_frame_pixels = 0;\n", 1)
video_path.write_text(video)

main_path = source / "main.c"
main_data = main_path.read_text()
marker = 'snprintf(fps_msg, sizeof(fps_msg), "FPS: %.1f (%.0f)", rendersps, vsyncsps);'
if main_data.count(marker) != 1:
    raise SystemExit("FPS HUD marker changed")
main_data = main_data.replace(marker,
    'if (!strcmp(core_name, "pcsx_rearmed"))\n'
    '\t\t\t\t\t\tsnprintf(fps_msg, sizeof(fps_msg), "FPS: %.0f DRAW: %.0f", vsyncsps, rendersps);\n'
    '\t\t\t\t\telse\n'
    '\t\t\t\t\t\t' + marker, 1)
main_path.write_text(main_data)

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
replace("main.c", "optimize_text = 1;", "optimize_text = 0;")
replace("options.c", "default_scale_effect = SCALE_EFFECT_SCANLINE;",
        "default_scale_effect = SCALE_EFFECT_NONE;")
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
