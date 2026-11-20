#ifndef PLUMOS_DRM_PAGEFLIP_H
#define PLUMOS_DRM_PAGEFLIP_H

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

struct plumos_drm_buffer {
  uint32_t handle;
  uint32_t fb_id;
  uint32_t pitch;
  uint64_t size;
  unsigned char *mem;
};

struct plumos_drm_pageflip {
  int fd;
  int active;
  int pending;
  int draw_index;
  uint32_t crtc_id;
  uint32_t connector_id;
  drmModeCrtc *original_crtc;
  struct plumos_drm_buffer buffers[2];
};

static void plumos_drm_pageflip_event(int fd, unsigned int frame,
                                      unsigned int sec, unsigned int usec,
                                      void *data) {
  struct plumos_drm_pageflip *d = data;
  (void)fd;
  (void)frame;
  (void)sec;
  (void)usec;
  if (d) d->pending = 0;
}

static void plumos_drm_pageflip_close(struct plumos_drm_pageflip *d) {
  int i;
  if (!d) return;
  if (d->fd >= 0 && d->active && d->original_crtc &&
      d->original_crtc->mode_valid) {
    (void)drmModeSetCrtc(d->fd, d->original_crtc->crtc_id,
                         d->original_crtc->buffer_id,
                         d->original_crtc->x, d->original_crtc->y,
                         &d->connector_id, 1, &d->original_crtc->mode);
  }
  if (d->original_crtc) {
    drmModeFreeCrtc(d->original_crtc);
    d->original_crtc = NULL;
  }
  if (d->fd >= 0) {
    for (i = 0; i < 2; i++) {
      struct plumos_drm_buffer *b = &d->buffers[i];
      if (b->mem && b->mem != MAP_FAILED) {
        munmap(b->mem, (size_t)b->size);
        b->mem = NULL;
      }
      if (b->fb_id) {
        (void)drmModeRmFB(d->fd, b->fb_id);
        b->fb_id = 0;
      }
      if (b->handle) {
        struct drm_mode_destroy_dumb destroy = {0};
        destroy.handle = b->handle;
        (void)drmIoctl(d->fd, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy);
        b->handle = 0;
      }
    }
    (void)drmDropMaster(d->fd);
    close(d->fd);
    d->fd = -1;
  }
  d->active = 0;
}

static int plumos_drm_pageflip_create_buffer(struct plumos_drm_pageflip *d,
                                              int index, uint32_t width,
                                              uint32_t height, uint32_t bpp) {
  struct drm_mode_create_dumb create = {0};
  struct drm_mode_map_dumb map = {0};
  struct plumos_drm_buffer *b = &d->buffers[index];
  create.width = width;
  create.height = height;
  create.bpp = bpp;
  if (drmIoctl(d->fd, DRM_IOCTL_MODE_CREATE_DUMB, &create) != 0) return 0;
  b->handle = create.handle;
  b->pitch = create.pitch;
  b->size = create.size;
  if (drmModeAddFB(d->fd, width, height, bpp == 16 ? 16 : 24, bpp, b->pitch,
                   b->handle, &b->fb_id) != 0) return 0;
  map.handle = b->handle;
  if (drmIoctl(d->fd, DRM_IOCTL_MODE_MAP_DUMB, &map) != 0) return 0;
  b->mem = mmap(NULL, (size_t)b->size, PROT_READ | PROT_WRITE,
                MAP_SHARED, d->fd, (off_t)map.offset);
  if (b->mem == MAP_FAILED) {
    b->mem = NULL;
    return 0;
  }
  memset(b->mem, 0, (size_t)b->size);
  return 1;
}

static int plumos_drm_pageflip_open_format(struct plumos_drm_pageflip *d,
                                           uint32_t width, uint32_t height,
                                           uint32_t bpp) {
  drmModeRes *res = NULL;
  drmModeConnector *connector = NULL;
  uint64_t dumb = 0;
  int i;
  memset(d, 0, sizeof(*d));
  d->fd = open("/dev/dri/card1", O_RDWR | O_CLOEXEC);
  if (d->fd < 0) return 0;
  if (drmSetMaster(d->fd) != 0 ||
      drmGetCap(d->fd, DRM_CAP_DUMB_BUFFER, &dumb) != 0 || !dumb) goto fail;
  res = drmModeGetResources(d->fd);
  if (!res) goto fail;
  for (i = 0; i < res->count_connectors; i++) {
    drmModeConnector *candidate =
        drmModeGetConnector(d->fd, res->connectors[i]);
    if (!candidate) continue;
    if (candidate->connection == DRM_MODE_CONNECTED &&
        candidate->count_modes > 0 && candidate->encoder_id) {
      connector = candidate;
      break;
    }
    drmModeFreeConnector(candidate);
  }
  if (!connector) goto fail;
  d->connector_id = connector->connector_id;
  {
    drmModeEncoder *encoder = drmModeGetEncoder(d->fd, connector->encoder_id);
    if (!encoder) goto fail;
    d->crtc_id = encoder->crtc_id;
    drmModeFreeEncoder(encoder);
  }
  d->original_crtc = drmModeGetCrtc(d->fd, d->crtc_id);
  if (!d->original_crtc || !d->original_crtc->mode_valid ||
      d->original_crtc->mode.hdisplay != width ||
      d->original_crtc->mode.vdisplay != height) goto fail;
  for (i = 0; i < 2; i++) {
    if (!plumos_drm_pageflip_create_buffer(d, i, width, height, bpp)) goto fail;
  }
  if (d->buffers[0].pitch != d->buffers[1].pitch ||
      d->buffers[0].size != d->buffers[1].size) goto fail;
  if (drmModeSetCrtc(d->fd, d->crtc_id, d->buffers[0].fb_id, 0, 0,
                     &d->connector_id, 1, &d->original_crtc->mode) != 0)
    goto fail;
  d->active = 1;
  d->draw_index = 1;
  drmModeFreeConnector(connector);
  drmModeFreeResources(res);
  fprintf(stderr, "drm-pageflip active %ux%u pitch=%u mode=%uHz\n",
          width, height, d->buffers[0].pitch,
          d->original_crtc->mode.vrefresh);
  return 1;
fail:
  fprintf(stderr, "drm-pageflip unavailable errno=%d\n", errno);
  if (connector) drmModeFreeConnector(connector);
  if (res) drmModeFreeResources(res);
  plumos_drm_pageflip_close(d);
  return 0;
}

static inline int plumos_drm_pageflip_open(struct plumos_drm_pageflip *d,
                                          uint32_t width, uint32_t height) {
  return plumos_drm_pageflip_open_format(d, width, height, 32);
}

static int plumos_drm_pageflip_present(struct plumos_drm_pageflip *d) {
  drmEventContext events = {0};
  struct pollfd pfd;
  int result;
  if (!d || !d->active) return 0;
  d->pending = 1;
  result = drmModePageFlip(d->fd, d->crtc_id,
                           d->buffers[d->draw_index].fb_id,
                           DRM_MODE_PAGE_FLIP_EVENT, d);
  if (result != 0) {
    d->pending = 0;
    return 0;
  }
  events.version = DRM_EVENT_CONTEXT_VERSION;
  events.page_flip_handler = plumos_drm_pageflip_event;
  pfd.fd = d->fd;
  pfd.events = POLLIN;
  pfd.revents = 0;
  while (d->pending) {
    result = poll(&pfd, 1, 1000);
    if (result <= 0 || drmHandleEvent(d->fd, &events) != 0) return 0;
  }
  d->draw_index ^= 1;
  return 1;
}

#endif
