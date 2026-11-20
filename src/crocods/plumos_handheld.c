#ifdef PLUMOS_HANDHELD

#include "plumos_handheld.h"
#include "plumos_drm_pageflip.h"

#include <SDL.h>
#include <linux/fb.h>
#include <linux/input.h>
#include <sys/ioctl.h>

static struct plumos_drm_pageflip display = { .fd = -1 };
static unsigned screen_width, screen_height;
static unsigned *source_columns;
static unsigned frame_width;
static int input_fd = -1;
static uint8_t keys[SDL_NUM_SCANCODES];

static const SDL_Scancode scancodes[KEY_MAX + 1] = {
    [KEY_UP] = SDL_SCANCODE_UP,             [KEY_DOWN] = SDL_SCANCODE_DOWN,
    [KEY_LEFT] = SDL_SCANCODE_LEFT,         [KEY_RIGHT] = SDL_SCANCODE_RIGHT,
    [KEY_LEFTCTRL] = SDL_SCANCODE_LCTRL,    [KEY_LEFTALT] = SDL_SCANCODE_LALT,
    [KEY_SPACE] = SDL_SCANCODE_SPACE,       [KEY_LEFTSHIFT] = SDL_SCANCODE_LSHIFT,
    [KEY_ESC] = SDL_SCANCODE_ESCAPE,        [KEY_ENTER] = SDL_SCANCODE_RETURN,
    [KEY_TAB] = SDL_SCANCODE_TAB,           [KEY_BACKSPACE] = SDL_SCANCODE_BACKSPACE,
    [KEY_PAGEUP] = SDL_SCANCODE_PAGEUP,     [KEY_PAGEDOWN] = SDL_SCANCODE_PAGEDOWN,
};

static int open_input(void)
{
    const char *event = getenv("PLUMOS_INPUT_EVENT");
    if (event && *event)
        return open(event, O_RDONLY | O_NONBLOCK | O_CLOEXEC);

    for (unsigned index = 0; index < 32; index++) {
        char device[64], name[128];
        snprintf(device, sizeof(device), "/dev/input/event%u", index);
        int fd = open(device, O_RDONLY | O_NONBLOCK | O_CLOEXEC);
        if (fd < 0)
            continue;
        if (ioctl(fd, EVIOCGNAME(sizeof(name)), name) >= 0 &&
            strcmp(name, "gpio-keys") == 0)
            return fd;
        close(fd);
    }
    return -1;
}

int plumos_crocods_open(void)
{
    struct fb_var_screeninfo mode = {0};
    int fb = open("/dev/fb0", O_RDONLY | O_CLOEXEC);
    if (fb < 0)
        return 0;
    int status = ioctl(fb, FBIOGET_VSCREENINFO, &mode);
    close(fb);
    if (status != 0 || !mode.xres || !mode.yres)
        return 0;

    input_fd = open_input();
    screen_width = mode.xres;
    screen_height = mode.yres;
    source_columns = malloc(screen_width * sizeof(*source_columns));
    if (input_fd < 0 || !source_columns ||
        !plumos_drm_pageflip_open_format(&display, screen_width, screen_height, 16)) {
        plumos_crocods_close();
        return 0;
    }
    return 1;
}

/* Collect the previous scanout event without waiting a full LCD refresh. */
static int collect_page_flip(int timeout)
{
    if (!display.pending)
        return 1;
    struct pollfd pfd = { .fd = display.fd, .events = POLLIN };
    int status = poll(&pfd, 1, timeout);
    if (status < 0 && errno == EINTR)
        return 0;
    if (status <= 0)
        return status;
    drmEventContext events = {
        .version = DRM_EVENT_CONTEXT_VERSION,
        .page_flip_handler = plumos_drm_pageflip_event,
    };
    if (!(pfd.revents & POLLIN) || drmHandleEvent(display.fd, &events) != 0)
        return -1;
    if (display.pending)
        return 0;
    display.draw_index ^= 1;
    return 1;
}

void plumos_crocods_close(void)
{
    if (input_fd >= 0) {
        close(input_fd);
        input_fd = -1;
    }
    free(source_columns);
    source_columns = NULL;
    frame_width = 0;
    (void)collect_page_flip(1000);
    plumos_drm_pageflip_close(&display);
}

const uint8_t *plumos_crocods_keys(void)
{
    struct input_event event;
    while (read(input_fd, &event, sizeof(event)) == sizeof(event)) {
        if (event.type == EV_SYN && event.code == SYN_DROPPED)
            memset(keys, 0, sizeof(keys));
        if (event.type == EV_KEY && event.code <= KEY_MAX && scancodes[event.code])
            keys[scancodes[event.code]] = event.value != 0;
    }
    return keys;
}

int plumos_crocods_present(const uint16_t *pixels, unsigned width, unsigned height)
{
    if (!pixels || !width || !height || !display.active)
        return 0;
    /* The LCD has about 3 ms of slack between 60 Hz scanout and 50 Hz CPC frames. */
    int ready = collect_page_flip(3);
    if (ready <= 0)
        return ready == 0;
    if (width != frame_width) {
        for (unsigned x = 0; x < screen_width; x++)
            source_columns[x] = x * width / screen_width;
        frame_width = width;
    }

    struct plumos_drm_buffer *buffer = &display.buffers[display.draw_index];
    unsigned previous_y = height;
    for (unsigned y = 0; y < screen_height; y++) {
        unsigned source_y = y * height / screen_height;
        uint16_t *output = (uint16_t *)(buffer->mem + y * buffer->pitch);
        if (source_y == previous_y) {
            memcpy(output, (unsigned char *)output - buffer->pitch,
                   screen_width * sizeof(*output));
        } else {
            const uint16_t *row = pixels + source_y * width;
            if (screen_width == width) {
                memcpy(output, row, width * sizeof(*row));
            } else if (screen_width == 2 * width) {
                uint32_t *pairs = (uint32_t *)output;
                for (unsigned x = 0; x < width; x++)
                    pairs[x] = (uint32_t)row[x] * UINT32_C(0x10001);
            } else {
                for (unsigned x = 0; x < screen_width; x++)
                    output[x] = row[source_columns[x]];
            }
            previous_y = source_y;
        }
    }
    if (drmModePageFlip(display.fd, display.crtc_id, buffer->fb_id,
                        DRM_MODE_PAGE_FLIP_EVENT, &display) != 0)
        return 0;
    display.pending = 1;
    return 1;
}

#endif
