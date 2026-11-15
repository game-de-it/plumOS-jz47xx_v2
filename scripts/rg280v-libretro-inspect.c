/* Read a libretro core's declared content types without starting video/audio. */
#include <dlfcn.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <libretro.h>

int main(int argc, char **argv)
{
    void *handle;
    void (*get_info)(struct retro_system_info *);
    unsigned (*api_version)(void);
    struct retro_system_info info = {0};

    if (argc != 2) return 2;
    alarm(8);
    handle = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        fprintf(stderr, "dlopen: %s\n", dlerror());
        return 3;
    }
    get_info = dlsym(handle, "retro_get_system_info");
    api_version = dlsym(handle, "retro_api_version");
    if (!get_info || !api_version) {
        fprintf(stderr, "missing libretro exports\n");
        return 4;
    }
    if (api_version() != RETRO_API_VERSION) {
        fprintf(stderr, "API mismatch: %u\n", api_version());
        return 5;
    }
    get_info(&info);
    printf("%s\t%s\t%s\t%d\n",
           info.library_name ? info.library_name : "",
           info.library_version ? info.library_version : "",
           info.valid_extensions ? info.valid_extensions : "",
           info.need_fullpath);
    return 0;
}
