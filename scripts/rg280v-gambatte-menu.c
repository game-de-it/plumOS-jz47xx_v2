/* Gambatte-DMS opens its menu on R1 or power. Keep those controls with
 * plumOS and open the emulator menu with SELECT+START instead. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <SDL/SDL.h>

int SDL_PollEvent(SDL_Event *event)
{
    typedef int (*poll_event_fn)(SDL_Event *);
    static poll_event_fn real_poll_event;
    static int select_down;
    static int start_down;
    static SDLKey menu_key;
    int result;

    if (!real_poll_event)
        real_poll_event = (poll_event_fn)dlsym(RTLD_NEXT, "SDL_PollEvent");
    if (!real_poll_event)
        return 0;

    while ((result = real_poll_event(event)) > 0) {
        if (event && (event->type == SDL_KEYDOWN || event->type == SDL_KEYUP)) {
            SDLKey key = event->key.keysym.sym;

            if (key == SDLK_HOME || key == SDLK_END || key == SDLK_BACKSPACE ||
                key == SDLK_RCTRL)
                continue;
            if (key == SDLK_ESCAPE || key == SDLK_RETURN) {
                int *down = key == SDLK_ESCAPE ? &select_down : &start_down;
                int was_down = *down;
                *down = event->type == SDL_KEYDOWN;

                if (*down && was_down && menu_key != SDLK_UNKNOWN)
                    continue;
                if (*down && !was_down && start_down && select_down) {
                    menu_key = key;
                    event->key.keysym.sym = SDLK_BACKSPACE;
                } else if (!*down && key == menu_key) {
                    menu_key = SDLK_UNKNOWN;
                    event->key.keysym.sym = SDLK_BACKSPACE;
                }
            }
        }
        return result;
    }
    return result;
}
