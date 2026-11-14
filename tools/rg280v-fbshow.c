#include <errno.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>

static int token(FILE *input, char *out, size_t size) {
    int ch;
    do {
        ch = fgetc(input);
        if (ch == '#') {
            while (ch != '\n' && ch != EOF) ch = fgetc(input);
        }
    } while (ch == ' ' || ch == '\n' || ch == '\r' || ch == '\t');
    if (ch == EOF) return -1;
    size_t length = 0;
    while (ch != EOF && ch != ' ' && ch != '\n' && ch != '\r' && ch != '\t') {
        if (length + 1 >= size) return -1;
        out[length++] = (char)ch;
        ch = fgetc(input);
    }
    out[length] = '\0';
    return 0;
}

static uint32_t channel(uint8_t value, struct fb_bitfield field) {
    if (!field.length) return 0;
    uint32_t maximum = (1u << field.length) - 1u;
    return (((uint32_t)value * maximum + 127u) / 255u) << field.offset;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: rg280v-fbshow image.ppm\n");
        return 2;
    }
    FILE *input = fopen(argv[1], "rb");
    if (!input) { perror(argv[1]); return 1; }
    char word[32];
    if (token(input, word, sizeof(word)) || strcmp(word, "P6") ||
        token(input, word, sizeof(word))) return 1;
    unsigned width = (unsigned)strtoul(word, NULL, 10);
    if (token(input, word, sizeof(word))) return 1;
    unsigned height = (unsigned)strtoul(word, NULL, 10);
    if (token(input, word, sizeof(word)) || strcmp(word, "255")) return 1;
    if (!width || !height || width > 4096 || height > 4096) return 1;
    size_t image_size = (size_t)width * height * 3;
    uint8_t *pixels = malloc(image_size);
    if (!pixels || fread(pixels, 1, image_size, input) != image_size) return 1;
    fclose(input);

    int fd = open("/dev/fb0", O_RDWR);
    if (fd < 0) { perror("/dev/fb0"); return 1; }
    struct fb_var_screeninfo var;
    struct fb_fix_screeninfo fix;
    if (ioctl(fd, FBIOGET_VSCREENINFO, &var) || ioctl(fd, FBIOGET_FSCREENINFO, &fix)) {
        perror("framebuffer info"); return 1;
    }
    if (var.bits_per_pixel != 16 && var.bits_per_pixel != 32) {
        fprintf(stderr, "unsupported bpp: %u\n", var.bits_per_pixel); return 1;
    }
    uint8_t *framebuffer = mmap(NULL, fix.smem_len, PROT_READ | PROT_WRITE,
                                MAP_SHARED, fd, 0);
    if (framebuffer == MAP_FAILED) { perror("mmap"); return 1; }
    unsigned bytes = var.bits_per_pixel / 8;
    unsigned draw_width = width < var.xres ? width : var.xres;
    unsigned draw_height = height < var.yres ? height : var.yres;
    for (unsigned page = 0; page * var.yres + draw_height <= var.yres_virtual; ++page) {
        for (unsigned y = 0; y < draw_height; ++y) {
            for (unsigned x = 0; x < draw_width; ++x) {
                size_t offset = ((size_t)page * var.yres + y) * fix.line_length + x * bytes;
                if (offset + bytes > fix.smem_len) continue;
                const uint8_t *rgb = pixels + ((size_t)y * width + x) * 3;
                uint32_t color = channel(rgb[0], var.red) | channel(rgb[1], var.green) |
                                 channel(rgb[2], var.blue) | channel(255, var.transp);
                memcpy(framebuffer + offset, &color, bytes);
            }
        }
    }
    msync(framebuffer, fix.smem_len, MS_SYNC);
    fprintf(stderr, "drew %ux%u on %ux%u, %u bpp, %u virtual rows\n",
            draw_width, draw_height, var.xres, var.yres, var.bits_per_pixel,
            var.yres_virtual);
    munmap(framebuffer, fix.smem_len);
    close(fd);
    free(pixels);
    return 0;
}
