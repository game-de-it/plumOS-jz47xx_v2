#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_mode.h>

int main(int argc, char **argv) {
    int fd = open("/dev/dri/card1", O_RDWR);
    if (fd < 0) { perror("open DRM"); return 1; }
    if (drmSetClientCap(fd, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1) != 0)
        perror("drmSetClientCap");
    if (drmSetClientCap(fd, DRM_CLIENT_CAP_ATOMIC, 1) != 0)
        perror("drmSetClientCap atomic");
    drmModeRes *res = drmModeGetResources(fd);
    if (!res) { perror("drmModeGetResources"); return 1; }
    uint32_t active_fb = 0;
    drmModePlaneRes *planes = drmModeGetPlaneResources(fd);
    if (planes) {
        for (uint32_t i = 0; i < planes->count_planes; ++i) {
            drmModePlane *p = drmModeGetPlane(fd, planes->planes[i]);
            if (p) {
                fprintf(stderr, "plane=%u crtc=%u fb=%u\n", p->plane_id,
                        p->crtc_id, p->fb_id);
                if (p->crtc_id && p->fb_id) {
                    active_fb = p->fb_id;
                    drmModeObjectProperties *properties = drmModeObjectGetProperties(
                        fd, p->plane_id, DRM_MODE_OBJECT_PLANE);
                    if (properties) {
                        for (uint32_t j = 0; j < properties->count_props; ++j) {
                            drmModePropertyRes *prop = drmModeGetProperty(
                                fd, properties->props[j]);
                            if (prop) {
                                if (strcmp(prop->name, "CRTC_X") == 0 ||
                                    strcmp(prop->name, "CRTC_Y") == 0 ||
                                    strcmp(prop->name, "CRTC_W") == 0 ||
                                    strcmp(prop->name, "CRTC_H") == 0 ||
                                    strcmp(prop->name, "sharpness") == 0)
                                    fprintf(stderr, "%s=%llu\n", prop->name,
                                            (unsigned long long)properties->prop_values[j]);
                                drmModeFreeProperty(prop);
                            }
                        }
                        drmModeFreeObjectProperties(properties);
                    }
                }
                drmModeFreePlane(p);
            }
        }
        drmModeFreePlaneResources(planes);
    } else perror("drmModeGetPlaneResources");
    for (int i = 0; i < res->count_crtcs; ++i) {
        drmModeCrtc *crtc = drmModeGetCrtc(fd, res->crtcs[i]);
        if (!crtc) { perror("drmModeGetCrtc"); continue; }
        fprintf(stderr, "crtc=%u fb=%u mode=%ux%u\n", crtc->crtc_id, crtc->buffer_id,
                crtc->width, crtc->height);
        uint32_t fb_id = crtc->buffer_id ? crtc->buffer_id : active_fb;
        if (!fb_id) { drmModeFreeCrtc(crtc); continue; }
        drmModeFB *fb = drmModeGetFB(fd, fb_id);
        if (!fb) { perror("drmModeGetFB"); drmModeFreeCrtc(crtc); continue; }
        drmModeFB2 *fb2 = drmModeGetFB2(fd, fb_id);
        if (fb2) {
            fprintf(stderr, "format=%.4s\n", (char *)&fb2->pixel_format);
            drmModeFreeFB2(fb2);
        } else perror("drmModeGetFB2");
        fprintf(stderr, "fb=%u size=%ux%u pitch=%u bpp=%u handle=%u\n",
                fb->fb_id, fb->width, fb->height, fb->pitch, fb->bpp, fb->handle);
        struct drm_mode_map_dumb map = { .handle = fb->handle };
        if (ioctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &map) < 0) {
            perror("DRM_IOCTL_MODE_MAP_DUMB"); return 2;
        }
        size_t size = (size_t)fb->pitch * fb->height;
        void *pixels = mmap(NULL, size, PROT_READ, MAP_SHARED, fd, map.offset);
        if (pixels == MAP_FAILED) { perror("mmap"); return 3; }
        int out = open(argc > 1 ? argv[1] : "/media/data/plumos/Logs/drm.raw",
                       O_CREAT | O_TRUNC | O_WRONLY, 0644);
        if (out < 0) { perror("open output"); return 4; }
        ssize_t n = write(out, pixels, size);
        fprintf(stderr, "wrote %zd of %zu bytes\n", n, size);
        close(out);
        munmap(pixels, size);
        drmModeFreeFB(fb);
        drmModeFreeCrtc(crtc);
        return n == (ssize_t)size ? 0 : 5;
    }
    return 6;
}
