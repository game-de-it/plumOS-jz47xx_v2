/* Temporary RG280V diagnostic: measure PicoArch's SDL_Flip blocking time. */
#define _GNU_SOURCE
#include <SDL/SDL.h>
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

static unsigned count;
static uint64_t total_ns;
static uint64_t min_ns = UINT64_MAX;
static uint64_t max_ns;
static unsigned waits_8ms;
static uint32_t flags;

static uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static void report(void)
{
    FILE *out;
    if (!count) return;
    out = fopen("/media/data/plumos/Logs/picoarch/vsync-probe.log", "a");
    if (!out) return;
    fprintf(out, "flips=%u flags=0x%08x doublebuf=%d avg_ms=%.3f min_ms=%.3f max_ms=%.3f waits_ge_8ms=%u\n",
            count, flags, !!(flags & SDL_DOUBLEBUF), (double)total_ns / count / 1e6,
            (double)min_ns / 1e6, (double)max_ns / 1e6, waits_8ms);
    fclose(out);
}

int SDL_Flip(SDL_Surface *surface)
{
    static int (*real_flip)(SDL_Surface *);
    uint64_t start, elapsed;
    int result;
    if (!real_flip) real_flip = dlsym(RTLD_NEXT, "SDL_Flip");
    if (!real_flip) return -1;
    start = now_ns();
    result = real_flip(surface);
    elapsed = now_ns() - start;
    flags = surface->flags;
    count++;
    total_ns += elapsed;
    if (elapsed < min_ns) min_ns = elapsed;
    if (elapsed > max_ns) max_ns = elapsed;
    if (elapsed >= 8000000ULL) waits_8ms++;
    if (count == 120 || count == 300) report();
    return result;
}
