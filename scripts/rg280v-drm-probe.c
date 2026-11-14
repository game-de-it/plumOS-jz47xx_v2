#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

int main(void) {
  int fd = open("/dev/dri/card1", O_RDWR | O_CLOEXEC);
  uint64_t cap = 0;
  drmModeRes *res;
  int i;
  if (fd < 0) {
    perror("open card1");
    return 1;
  }
  printf("dumb_buffer=%d cap=%llu\n", drmGetCap(fd, DRM_CAP_DUMB_BUFFER, &cap),
         (unsigned long long)cap);
  res = drmModeGetResources(fd);
  if (!res) {
    perror("drmModeGetResources");
    return 1;
  }
  printf("connectors=%d crtcs=%d\n", res->count_connectors, res->count_crtcs);
  for (i = 0; i < res->count_connectors; i++) {
    drmModeConnector *conn = drmModeGetConnector(fd, res->connectors[i]);
    if (!conn) continue;
    printf("connector=%u state=%d encoder=%u modes=%d\n", conn->connector_id,
           conn->connection, conn->encoder_id, conn->count_modes);
    for (int j = 0; j < conn->count_modes; j++) {
      drmModeModeInfo *m = &conn->modes[j];
      printf(" mode=%s %ux%u clock=%u htotal=%u vtotal=%u vrefresh=%u\n",
             m->name, m->hdisplay, m->vdisplay, m->clock, m->htotal,
             m->vtotal, m->vrefresh);
    }
    drmModeFreeConnector(conn);
  }
  for (i = 0; i < res->count_crtcs; i++) {
    drmModeCrtc *crtc = drmModeGetCrtc(fd, res->crtcs[i]);
    if (!crtc) continue;
    printf("crtc=%u fb=%u mode_valid=%d\n", crtc->crtc_id,
           crtc->buffer_id, crtc->mode_valid);
    drmModeFreeCrtc(crtc);
  }
  drmModeFreeResources(res);
  close(fd);
  return 0;
}
