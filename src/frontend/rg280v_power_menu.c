/* Draw the plumOS power menu on a separate buffer of the game's DRM plane. */
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <signal.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
#include <drm.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#define PLUMOS_FBDEV_RENDERER_GLYPHS_ONLY
#include "plumos_fbdev_renderer.h"

#define CARD "/dev/dri/card1"
#define SHUTDOWN "/media/data/plumos/bin/plumos-safe-shutdown"

static volatile sig_atomic_t interrupted;
static void on_signal(int signal_number) { (void)signal_number; interrupted = 1; }

struct plane_state {
  uint32_t plane, crtc, framebuffer;
  int crtc_x, crtc_y;
  uint32_t crtc_w, crtc_h, src_x, src_y, src_w, src_h;
  uint32_t width, height, depth, bpp;
};

static int save_plane(int fd, struct plane_state *state) {
  drmModePlaneRes *planes;
  uint32_t i;
  memset(state, 0, sizeof(*state));
  (void)drmSetClientCap(fd, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1);
  planes = drmModeGetPlaneResources(fd);
  if (!planes) return 0;
  for (i = 0; i < planes->count_planes; i++) {
    drmModePlane *plane = drmModeGetPlane(fd, planes->planes[i]);
    drmModeFB *fb;
    drmModeCrtc *crtc;
    drmModeObjectProperties *properties;
    uint32_t j;
    if (!plane) continue;
    if (!plane->crtc_id || !plane->fb_id) { drmModeFreePlane(plane); continue; }
    fb = drmModeGetFB(fd, plane->fb_id);
    crtc = drmModeGetCrtc(fd, plane->crtc_id);
    if (!fb || !crtc) {
      if (fb) drmModeFreeFB(fb);
      if (crtc) drmModeFreeCrtc(crtc);
      drmModeFreePlane(plane);
      continue;
    }
    state->plane = plane->plane_id;
    state->crtc = plane->crtc_id;
    state->framebuffer = plane->fb_id;
    state->width = fb->width;
    state->height = fb->height;
    state->depth = fb->depth;
    state->bpp = fb->bpp;
    state->crtc_w = crtc->width;
    state->crtc_h = crtc->height;
    state->src_w = fb->width << 16;
    state->src_h = fb->height << 16;
    properties = drmModeObjectGetProperties(fd, state->plane, DRM_MODE_OBJECT_PLANE);
    if (properties) {
      for (j = 0; j < properties->count_props; j++) {
        drmModePropertyRes *prop = drmModeGetProperty(fd, properties->props[j]);
        uint64_t value = properties->prop_values[j];
        if (!prop) continue;
        if (strcmp(prop->name, "CRTC_X") == 0) state->crtc_x = (int)value;
        else if (strcmp(prop->name, "CRTC_Y") == 0) state->crtc_y = (int)value;
        else if (strcmp(prop->name, "CRTC_W") == 0) state->crtc_w = (uint32_t)value;
        else if (strcmp(prop->name, "CRTC_H") == 0) state->crtc_h = (uint32_t)value;
        else if (strcmp(prop->name, "SRC_X") == 0) state->src_x = (uint32_t)value;
        else if (strcmp(prop->name, "SRC_Y") == 0) state->src_y = (uint32_t)value;
        else if (strcmp(prop->name, "SRC_W") == 0) state->src_w = (uint32_t)value;
        else if (strcmp(prop->name, "SRC_H") == 0) state->src_h = (uint32_t)value;
        drmModeFreeProperty(prop);
      }
      drmModeFreeObjectProperties(properties);
    }
    drmModeFreeFB(fb);
    drmModeFreeCrtc(crtc);
    drmModeFreePlane(plane);
    break;
  }
  drmModeFreePlaneResources(planes);
  return state->framebuffer != 0;
}

static int restore_plane(int fd, const struct plane_state *state) {
  return drmModeSetPlane(fd, state->plane, state->crtc, state->framebuffer, 0,
                         state->crtc_x, state->crtc_y,
                         state->crtc_w, state->crtc_h,
                         state->src_x, state->src_y,
                         state->src_w, state->src_h) == 0;
}

struct menu_buffer {
  uint32_t handle, framebuffer, pitch;
  uint64_t size;
  uint8_t *pixels;
};

static void destroy_buffer(int fd, struct menu_buffer *b) {
  struct drm_mode_destroy_dumb destroy = {0};
  if (b->framebuffer) drmModeRmFB(fd, b->framebuffer);
  if (b->pixels) munmap(b->pixels, (size_t)b->size);
  if (b->handle) {
    destroy.handle = b->handle;
    drmIoctl(fd, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy);
  }
  memset(b, 0, sizeof(*b));
}

static int create_buffer(int fd, const struct plane_state *p, struct menu_buffer *b) {
  struct drm_mode_create_dumb create = {0};
  struct drm_mode_map_dumb map = {0};
  memset(b, 0, sizeof(*b));
  if ((p->bpp != 16 && p->bpp != 32) || p->width < 240 || p->height < 160) return 0;
  create.width = p->width;
  create.height = p->height;
  create.bpp = p->bpp;
  if (drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &create) != 0) return 0;
  b->handle = create.handle;
  b->pitch = create.pitch;
  b->size = create.size;
  if (drmModeAddFB(fd, p->width, p->height, p->depth, p->bpp,
                   b->pitch, b->handle, &b->framebuffer) != 0) goto fail;
  map.handle = b->handle;
  if (drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &map) != 0) goto fail;
  b->pixels = mmap(NULL, (size_t)b->size, PROT_READ | PROT_WRITE,
                   MAP_SHARED, fd, (off_t)map.offset);
  if (b->pixels == MAP_FAILED) { b->pixels = NULL; goto fail; }
  return 1;
fail:
  destroy_buffer(fd, b);
  return 0;
}

static uint32_t rgb(const struct plane_state *p, unsigned r, unsigned g, unsigned b) {
  if (p->bpp == 32) return (r << 16) | (g << 8) | b;
  if (p->depth == 15) return ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3);
  return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3);
}

static void rect(const struct plane_state *p, struct menu_buffer *b,
                 int x, int y, int w, int h, uint32_t color) {
  int xx, yy;
  if (x < 0) { w += x; x = 0; }
  if (y < 0) { h += y; y = 0; }
  if (x + w > (int)p->width) w = (int)p->width - x;
  if (y + h > (int)p->height) h = (int)p->height - y;
  for (yy = y; yy < y + h; yy++) {
    if (p->bpp == 32) {
      uint32_t *row = (uint32_t *)(b->pixels + (size_t)yy * b->pitch);
      for (xx = x; xx < x + w; xx++) row[xx] = color;
    } else {
      uint16_t *row = (uint16_t *)(b->pixels + (size_t)yy * b->pitch);
      for (xx = x; xx < x + w; xx++) row[xx] = (uint16_t)color;
    }
  }
}

static void label(const struct plane_state *p, struct menu_buffer *b,
                  int x, int y, const char *s, int scale, uint32_t color) {
  for (; *s; s++, x += 6 * scale) {
    const uint8_t *glyph = plumos_fbdev_glyph_for(*s);
    int row, col;
    for (row = 0; row < 7; row++)
      for (col = 0; col < 5; col++)
        if (glyph[row] & (1U << (4 - col)))
          rect(p, b, x + col * scale, y + row * scale, scale, scale, color);
  }
}

static void draw_menu(const struct plane_state *p, struct menu_buffer *b, int cursor) {
  static const char *names[] = {"Sleep", "Reboot", "Shutdown", "Cancel"};
  int row, scale = p->width >= 320 ? 2 : 1;
  int gap = (int)p->height >= 240 ? (int)p->height / 10 : 20;
  int top = (int)p->height * 13 / 30;
  uint32_t bg = rgb(p, 5, 8, 10), fg = rgb(p, 232, 242, 238);
  uint32_t muted = rgb(p, 137, 160, 166), accent = rgb(p, 255, 132, 13);
  uint32_t selected = rgb(p, 35, 58, 51), yellow = rgb(p, 255, 230, 122);
  rect(p, b, 0, 0, p->width, p->height, bg);
  rect(p, b, 0, 0, 4, 35, accent);
  label(p, b, 12, 10, "PLUMOS", scale, fg);
  label(p, b, (int)p->width - 84, 10, "RG280V", scale, fg);
  rect(p, b, 0, 34, p->width, 2, rgb(p, 35, 58, 51));
  label(p, b, 12, 47, "POWER", scale, muted);
  for (row = 0; row < 4; row++) {
    int y = top + row * gap;
    if (row == cursor) rect(p, b, 9, y - 8, (int)p->width - 18, gap + 1, selected);
    label(p, b, 20, y, row == cursor ? ">" : " ", scale,
          row == cursor ? yellow : muted);
    label(p, b, 40, y, names[row], scale, row == cursor ? yellow : fg);
  }
  (void)msync(b->pixels, (size_t)b->size, MS_SYNC);
}

static int show_buffer(int fd, const struct plane_state *p, const struct menu_buffer *b) {
  return drmModeSetPlane(fd, p->plane, p->crtc, b->framebuffer, 0,
                         p->crtc_x, p->crtc_y, p->crtc_w, p->crtc_h,
                         p->src_x, p->src_y, p->src_w, p->src_h) == 0;
}

static int drm_fd_for_pid(pid_t pid) {
  char path[320], link[128], comm[80];
  struct dirent *entry;
  FILE *f;
  DIR *dir;
  int result = -1;
  snprintf(path, sizeof(path), "/proc/%ld/comm", (long)pid);
  f = fopen(path, "r");
  if (!f) return -1;
  if (!fgets(comm, sizeof(comm), f)) { fclose(f); return -1; }
  fclose(f);
  if (strncmp(comm, "plumos-control", 14) == 0 ||
      strncmp(comm, "plumos-rg280v", 13) == 0 ||
      strncmp(comm, "rg280v-drm", 10) == 0) return -1;
  snprintf(path, sizeof(path), "/proc/%ld/fd", (long)pid);
  dir = opendir(path);
  if (!dir) return -1;
  while ((entry = readdir(dir))) {
    char *end;
    long number = strtol(entry->d_name, &end, 10);
    ssize_t n;
    if (*end || number < 0 || number > 1024) continue;
    snprintf(path, sizeof(path), "/proc/%ld/fd/%ld", (long)pid, number);
    n = readlink(path, link, sizeof(link) - 1);
    if (n < 0) continue;
    link[n] = '\0';
    if (strcmp(link, CARD) == 0) { result = (int)number; break; }
  }
  closedir(dir);
  return result;
}

static pid_t display_owner(int *remote_fd) {
  struct dirent *entry;
  DIR *dir = opendir("/proc");
  pid_t owner = 0;
  if (!dir) return 0;
  while ((entry = readdir(dir))) {
    char *end;
    long pid = strtol(entry->d_name, &end, 10);
    int fd;
    if (*end || pid <= 1 || pid == getpid()) continue;
    fd = drm_fd_for_pid((pid_t)pid);
    if (fd >= 0) { owner = (pid_t)pid; *remote_fd = fd; break; }
  }
  closedir(dir);
  return owner;
}

static int run_power_action(const char *action) {
  pid_t child = fork();
  int status;
  if (child < 0) return 0;
  if (child == 0) {
    if (strcmp(action, "sleep") == 0)
      execl(SHUTDOWN, SHUTDOWN, "--sleep", (char *)NULL);
    else if (strcmp(action, "reboot") == 0)
      execl(SHUTDOWN, SHUTDOWN, "--reboot", (char *)NULL);
    else
      execl(SHUTDOWN, SHUTDOWN, "--shutdown", (char *)NULL);
    _exit(127);
  }
  if (waitpid(child, &status, 0) != child) return 0;
  return WIFEXITED(status) && WEXITSTATUS(status) == 0;
}

int main(int argc, char **argv) {
  static const char *actions[] = {"sleep", "reboot", "shutdown", "cancel"};
  pid_t owner;
  struct plane_state original_plane;
  struct menu_buffer buffers[2] = {{0}};
  struct input_event event;
  struct pollfd input_poll;
  int remote_fd = -1, pidfd = -1, drmfd = -1, inputfd = -1;
  int cursor = 3, visible = 0, result = 1, selected = 3, elapsed = 0;
  int probe = argc > 1 && strcmp(argv[1], "--probe") == 0;
  signal(SIGTERM, on_signal);
  signal(SIGINT, on_signal);
  owner = display_owner(&remote_fd);
  if (!owner) return 2; /* The FE receives its own power event. */
  pidfd = syscall(SYS_pidfd_open, owner, 0);
  if (pidfd < 0) goto done;
  drmfd = syscall(SYS_pidfd_getfd, pidfd, remote_fd, 0);
  if (drmfd < 0) goto done;
  if (kill(owner, SIGSTOP) != 0) goto done;
  usleep(30000);
  if (!save_plane(drmfd, &original_plane)) goto resume;
  if (!create_buffer(drmfd, &original_plane, &buffers[0]) ||
      !create_buffer(drmfd, &original_plane, &buffers[1])) goto restore;
  inputfd = open("/dev/input/event2", O_RDONLY | O_CLOEXEC);
  if (inputfd < 0) goto restore;
  draw_menu(&original_plane, &buffers[visible], cursor);
  if (!show_buffer(drmfd, &original_plane, &buffers[visible])) goto restore;
  input_poll.fd = inputfd;
  input_poll.events = POLLIN;
  result = 0;
  while (!interrupted) {
    int n = poll(&input_poll, 1, 100);
    if (probe) { elapsed += 100; if (elapsed >= 3000) break; }
    if (n < 0) { if (errno == EINTR) continue; result = 1; break; }
    if (n == 0) continue;
    if (read(inputfd, &event, sizeof(event)) != sizeof(event)) { result = 1; break; }
    if (event.type != EV_KEY || event.value != 1) continue;
    if (event.code == KEY_UP && cursor > 0) cursor--;
    else if (event.code == KEY_DOWN && cursor < 3) cursor++;
    else if (event.code == KEY_LEFTALT || event.code == KEY_ESC || event.code == KEY_POWER) break;
    else if (event.code == KEY_LEFTCTRL) { selected = cursor; break; }
    else continue;
    draw_menu(&original_plane, &buffers[visible ^ 1], cursor);
    if (!show_buffer(drmfd, &original_plane, &buffers[visible ^ 1])) { result = 1; break; }
    visible ^= 1;
  }
restore:
  if (!restore_plane(drmfd, &original_plane)) {
    fprintf(stderr, "power menu: cannot restore game plane: %s\n", strerror(errno));
    result = 1;
  }
  destroy_buffer(drmfd, &buffers[0]);
  destroy_buffer(drmfd, &buffers[1]);
  if (!probe && result == 0 && selected != 3)
    (void)run_power_action(actions[selected]);
resume:
  kill(owner, SIGCONT);
done:
  if (inputfd >= 0) close(inputfd);
  if (drmfd >= 0) close(drmfd);
  if (pidfd >= 0) close(pidfd);
  return result;
}
