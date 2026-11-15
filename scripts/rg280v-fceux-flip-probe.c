/* Temporary SDL_Flip timing probe for the RG280V standalone FCEUX. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct SDL_Surface SDL_Surface;

static uint64_t nanoseconds(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000u + ts.tv_nsec;
}

int SDL_Flip(SDL_Surface *surface)
{
    typedef int (*flip_fn)(SDL_Surface *);
    static flip_fn real_flip;
    static uint64_t window_start, flip_total, flip_max;
    static unsigned flips;
    uint64_t before, after, duration;
    const char *path;
    int result;

    if (!real_flip)
        real_flip = (flip_fn)dlsym(RTLD_NEXT, "SDL_Flip");
    if (!real_flip)
        return -1;
    before = nanoseconds();
    result = real_flip(surface);
    after = nanoseconds();
    duration = after - before;
    if (!window_start)
        window_start = before;
    flips++;
    flip_total += duration;
    if (duration > flip_max)
        flip_max = duration;
    if (after - window_start >= 2000000000u) {
        path = getenv("PLUMOS_FCEUX_FLIP_LOG");
        if (path && *path) {
            FILE *file = fopen(path, "a");
            if (file) {
                fprintf(file, "%.3f\t%u\t%.2f\t%.3f\t%.3f\n",
                        (after - window_start) / 1000000000.0, flips,
                        flips * 1000000000.0 / (after - window_start),
                        flip_total / (1000000.0 * flips),
                        flip_max / 1000000.0);
                fclose(file);
            }
        }
        window_start = after;
        flip_total = flip_max = 0;
        flips = 0;
    }
    return result;
}
