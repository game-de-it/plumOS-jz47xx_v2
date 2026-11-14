/* ReGBA draws its decorative border only during the first three frames.
 * The RG280V SDL/KMSDRM triple-buffer path may display an unpainted buffer
 * later. Use synchronous double buffering for ReGBA's video modes. */
#define _GNU_SOURCE
#include <stdint.h>
#include <dlfcn.h>

void *SDL_SetVideoMode(int width, int height, int bpp, uint32_t flags)
{
    typedef void *(*set_video_mode_fn)(int, int, int, uint32_t);
    static set_video_mode_fn real_set_video_mode;

    if (!real_set_video_mode)
        real_set_video_mode = (set_video_mode_fn)dlsym(RTLD_NEXT, "SDL_SetVideoMode");
    if (!real_set_video_mode)
        return 0;

    /* SDL_TRIPLEBUF is SDL_DOUBLEBUF | 0x100 in this OpenDingux SDL 1.2. */
    flags &= ~UINT32_C(0x100);
    return real_set_video_mode(width, height, bpp, flags);
}
