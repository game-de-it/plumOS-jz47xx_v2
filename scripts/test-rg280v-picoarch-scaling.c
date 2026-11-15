/* Exercise the real PicoArch scaler after scripts/patch-rg280v-picoarch.py. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "scale.h"
#include "main.h"

double aspect_ratio;
enum scale_size scale_size;
enum scale_effect scale_effect;
int optimize_text;

void pa_log(enum retro_log_level level, const char *fmt, ...)
{
    (void)level;
    (void)fmt;
}

static int check(unsigned w, unsigned h, double ratio, enum scale_size mode,
                 unsigned expected_w, unsigned expected_h)
{
    uint16_t *src = malloc((size_t)w * h * sizeof(*src));
    uint16_t dst[SCREEN_WIDTH * SCREEN_HEIGHT];
    unsigned min_x = SCREEN_WIDTH, min_y = SCREEN_HEIGHT, max_x = 0, max_y = 0;
    if (!src) return 1;
    memset(src, 0xff, (size_t)w * h * sizeof(*src));
    memset(dst, 0xa5, sizeof(dst)); /* Detect uncleared double-buffer margins. */
    aspect_ratio = ratio;
    scale_size = mode;
    scale_effect = SCALE_EFFECT_NONE;
    scale_update_scaler();
    scale(w, h, (size_t)w * sizeof(*src), src, dst);
    for (unsigned y = 0; y < SCREEN_HEIGHT; y++) {
        for (unsigned x = 0; x < SCREEN_WIDTH; x++) {
            if (dst[(size_t)y * SCREEN_WIDTH + x]) {
                if (x < min_x) min_x = x;
                if (x > max_x) max_x = x;
                if (y < min_y) min_y = y;
                if (y > max_y) max_y = y;
            }
        }
    }
    free(src);
    unsigned actual_w = max_x - min_x + 1, actual_h = max_y - min_y + 1;
    printf("%ux%u ratio=%.3f mode=%d => %ux%u\n",
           w, h, ratio, mode, actual_w, actual_h);
    return actual_w != expected_w || actual_h != expected_h;
}

int main(void)
{
    int failures = 0;
    failures += check(160, 144, 0, SCALE_SIZE_NONE, 160, 144);
    failures += check(160, 144, 0, SCALE_SIZE_ASPECT, 267, 240);
    failures += check(160, 144, 0, SCALE_SIZE_FULL, 320, 240);
    failures += check(256, 192, 0, SCALE_SIZE_NONE, 256, 192);
    failures += check(256, 192, 0, SCALE_SIZE_ASPECT, 320, 240);
    failures += check(256, 192, 0, SCALE_SIZE_FULL, 320, 240);
    failures += check(240, 160, 0, SCALE_SIZE_ASPECT, 320, 213);
    failures += check(240, 160, 0, SCALE_SIZE_FULL, 320, 240);
    failures += check(160, 144, 1.333333, SCALE_SIZE_ASPECT, 320, 240);
    failures += check(320, 224, 1.333333, SCALE_SIZE_NONE, 320, 224);
    failures += check(640, 480, 0, SCALE_SIZE_NONE, 320, 240);
    printf("failures=%d\n", failures);
    return !!failures;
}
