#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <SDL/SDL.h>

SDL_Surface *SDL_SetVideoMode(int width, int height, int bpp, Uint32 flags)
{
    typedef SDL_Surface *(*fn)(int, int, int, Uint32);
    static fn real;
    if (!real)
        real = (fn)dlsym(RTLD_NEXT, "SDL_SetVideoMode");
    SDL_Surface *surface = real ? real(width, height, bpp, flags) : NULL;
    fprintf(stderr, "SDL_MODE request=%dx%dx%d flags=%08x result=%p", width, height,
            bpp, (unsigned)flags, (void *)surface);
    if (surface && surface->format)
        fprintf(stderr, " actual=%dx%dx%d pitch=%u masks=%08x/%08x/%08x/%08x",
                surface->w, surface->h, surface->format->BitsPerPixel,
                (unsigned)surface->pitch, surface->format->Rmask, surface->format->Gmask,
                surface->format->Bmask, surface->format->Amask);
    fputc('\n', stderr);
    return surface;
}

int SDL_Flip(SDL_Surface *surface)
{
    typedef int (*fn)(SDL_Surface *);
    static fn real;
    static void *last_pixels;
    static unsigned changes;
    if (!real)
        real = (fn)dlsym(RTLD_NEXT, "SDL_Flip");
    void *before = surface ? surface->pixels : NULL;
    int result = real ? real(surface) : -1;
    void *after = surface ? surface->pixels : NULL;
    if ((before != after || (last_pixels && before != last_pixels)) && changes++ < 12)
        fprintf(stderr, "SDL_FLIP pixels before=%p after=%p previous=%p\n",
                before, after, last_pixels);
    last_pixels = after;
    return result;
}
