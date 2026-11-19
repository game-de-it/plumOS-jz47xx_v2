/* FCEUX's GCW Zero build opens its menu on SDL HOME. RG280V reserves the
 * physical power button for plumOS; use SELECT+START for the emulator menu. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdlib.h>
#include <string.h>
#include <SDL/SDL.h>

/* The legacy frontend checks SDL_VideoModeOK before SDL_SetVideoMode.
 * OpenDingux's KMSDRM backend can scale a 320x240 surface, but the public
 * SDL 1.2 check only lists physical panel modes (640x480 on RG300X).
 * Match the legacy software/native NES modes only; retain other SDL answers. */
int SDL_VideoModeOK(int width, int height, int bpp, Uint32 flags)
{
    typedef int (*mode_ok_fn)(int, int, int, Uint32);
    typedef char *(*driver_name_fn)(char *, int);
    typedef const SDL_VideoInfo *(*video_info_fn)(void);
    typedef SDL_Rect **(*list_modes_fn)(SDL_PixelFormat *, Uint32);
    static mode_ok_fn real_mode_ok;
    static driver_name_fn driver_name;
    static video_info_fn video_info;
    static list_modes_fn list_modes;
    const char *enabled = getenv("PLUMOS_FCEUX_LEGACY_MODE_CHECK");
    const SDL_VideoInfo *info;
    SDL_Rect **modes;
    char driver[32];
    int result;
    int legacy_mode = (width == 320 && height == 240) ||
        ((width == 240 || width == 256) && (height == 224 || height == 240)) ||
        (width == 280 && height == 240);

    if (!real_mode_ok) real_mode_ok = (mode_ok_fn)dlsym(RTLD_NEXT, "SDL_VideoModeOK");
    if (!real_mode_ok) return 0;
    result = real_mode_ok(width, height, bpp, flags);
    if (result || !enabled || strcmp(enabled, "1") ||
        !legacy_mode || bpp != 16) return result;
    if (!driver_name) driver_name = (driver_name_fn)dlsym(RTLD_NEXT, "SDL_VideoDriverName");
    if (!video_info) video_info = (video_info_fn)dlsym(RTLD_NEXT, "SDL_GetVideoInfo");
    if (!list_modes) list_modes = (list_modes_fn)dlsym(RTLD_NEXT, "SDL_ListModes");
    if (!driver_name || !video_info || !list_modes || !driver_name(driver, sizeof(driver)) ||
        strcmp(driver, "kmsdrm")) return result;
    info = video_info();
    if (!info) return result;
    /* current_w/h describe the last application surface after a mode switch,
     * not the panel. Consult the backend list so native -> software still works. */
    modes = list_modes(NULL, flags);
    if (modes == (SDL_Rect **)-1) return bpp;
    if (modes) {
        for (int i = 0; modes[i]; ++i)
            if (modes[i]->w >= width && modes[i]->h >= height) return bpp;
    }
    return result;
}

int SDL_PollEvent(SDL_Event *event)
{
    typedef int (*poll_event_fn)(SDL_Event *);
    static poll_event_fn real_poll_event;
    static int select_down;
    static int combo_down;
    int result;

    if (!real_poll_event)
        real_poll_event = (poll_event_fn)dlsym(RTLD_NEXT, "SDL_PollEvent");
    if (!real_poll_event)
        return 0;

    while ((result = real_poll_event(event)) > 0) {
        if (event && (event->type == SDL_KEYDOWN || event->type == SDL_KEYUP)) {
            SDLKey key = event->key.keysym.sym;

            if (key == SDLK_HOME)
                continue;
            if (key == SDLK_ESCAPE)
                select_down = event->type == SDL_KEYDOWN;
            if (key == SDLK_RETURN) {
                if (event->type == SDL_KEYDOWN && select_down) {
                    combo_down = 1;
                    event->key.keysym.sym = SDLK_HOME;
                } else if (event->type == SDL_KEYUP && combo_down) {
                    combo_down = 0;
                    event->key.keysym.sym = SDLK_HOME;
                }
            }
        }
        return result;
    }
    return result;
}
