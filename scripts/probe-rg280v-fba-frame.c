/* Capture one SDL 1.2 frame before FBA hands it to the RG280V video driver. */
#define _GNU_SOURCE
#include <SDL/SDL.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdint.h>

static int (*real_flip)(SDL_Surface *);
static unsigned int flips;

int SDL_Flip(SDL_Surface *surface)
{
    if (!real_flip)
        real_flip = (int (*)(SDL_Surface *)) dlsym(RTLD_NEXT, "SDL_Flip");
    if (surface && ++flips == 120) {
        FILE *meta = fopen("/tmp/rg350-fba-frame.txt", "w");
        FILE *raw = fopen("/tmp/rg350-fba-frame.raw", "wb");
        int locked = SDL_MUSTLOCK(surface);
        if (locked && SDL_LockSurface(surface) != 0)
            locked = -1;
        if (meta) {
            fprintf(meta, "w=%d h=%d pitch=%u bpp=%u flags=%08x "
                    "rmask=%08x gmask=%08x bmask=%08x\n",
                    surface->w, surface->h, surface->pitch,
                    surface->format->BitsPerPixel, surface->flags,
                    surface->format->Rmask, surface->format->Gmask,
                    surface->format->Bmask);
            fclose(meta);
        }
        if (raw) {
            if (locked >= 0)
                fwrite(surface->pixels, surface->pitch, surface->h, raw);
            fclose(raw);
        }
        if (locked > 0)
            SDL_UnlockSurface(surface);
    }
    return real_flip ? real_flip(surface) : -1;
}
