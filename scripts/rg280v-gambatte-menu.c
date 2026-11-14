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
    static int combo_down;
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
            if (key == SDLK_ESCAPE)
                select_down = event->type == SDL_KEYDOWN;
            if (key == SDLK_RETURN) {
                if (event->type == SDL_KEYDOWN && select_down) {
                    combo_down = 1;
                    event->key.keysym.sym = SDLK_BACKSPACE;
                } else if (event->type == SDL_KEYUP && combo_down) {
                    combo_down = 0;
                    event->key.keysym.sym = SDLK_BACKSPACE;
                }
            }
        }
        return result;
    }
    return result;
}
