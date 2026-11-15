/* Temporary telemetry for unattended RG280V PicoArch smoke tests. */
#define _GNU_SOURCE
#include <SDL/SDL.h>
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static void (*original_audio)(void *, Uint8 *, int);
static void *original_audio_data;
static unsigned audio_callbacks;
static uint64_t audio_frames, audio_zero, audio_clipped, audio_energy;
static unsigned audio_peak;
static unsigned audio_rate, audio_channels, audio_format;
static uint64_t audio_first, audio_last;
static unsigned flips;
static uint64_t flip_first, flip_last, flip_wait_ns, flip_max_ns;
static unsigned flip_waits_8ms;
static unsigned flip_report_count;
static uint64_t flip_report_time;

static uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

static void report(const char *kind)
{
    const char *path = getenv("PLUMOS_PICOARCH_HEALTH_LOG");
    FILE *out;
    if (!path || !(out = fopen(path, "a"))) return;
    if (kind[0] == 'v') {
        fprintf(out, "video\tflips=%u\tfps=%.2f\tfps_window=%.2f\tflip_avg_ms=%.3f\tflip_max_ms=%.3f\twaits_ge_8ms=%u\n",
                flips, flips > 1 ? (double)(flips - 1) * 1e9 / (flip_last - flip_first) : 0.0,
                flip_report_count && flip_last > flip_report_time
                    ? (double)(flips - flip_report_count) * 1e9 / (flip_last - flip_report_time)
                    : (flips > 1 ? (double)(flips - 1) * 1e9 / (flip_last - flip_first) : 0.0),
                flips ? (double)flip_wait_ns / flips / 1e6 : 0.0,
                (double)flip_max_ns / 1e6, flip_waits_8ms);
    } else {
        fprintf(out, "audio\tcallbacks=%u\trate=%u\tchannels=%u\tformat=0x%x\tframes=%llu\tseconds=%.3f\tzero_frac=%.4f\tclipped_frac=%.4f\tpeak=%u\tenergy=%llu\n",
                audio_callbacks, audio_rate, audio_channels, audio_format,
                (unsigned long long)audio_frames,
                audio_last > audio_first ? (double)(audio_last - audio_first) / 1e9 : 0.0,
                audio_frames ? (double)audio_zero / (audio_frames * audio_channels) : 0.0,
                audio_frames ? (double)audio_clipped / (audio_frames * audio_channels) : 0.0,
                audio_peak, (unsigned long long)audio_energy);
    }
    fclose(out);
    if (kind[0] == 'v') {
        flip_report_count = flips;
        flip_report_time = flip_last;
    }
}

static void audio_callback(void *ignored, Uint8 *stream, int len)
{
    unsigned samples, i;
    const int16_t *pcm;
    (void)ignored;
    if (original_audio) original_audio(original_audio_data, stream, len);
    audio_last = now_ns();
    if (!audio_first) audio_first = audio_last;
    audio_callbacks++;
    if (audio_format == AUDIO_S16LSB && audio_channels) {
        samples = (unsigned)len / sizeof(int16_t);
        pcm = (const int16_t *)stream;
        for (i = 0; i < samples; i++) {
            int sample = pcm[i];
            unsigned magnitude = sample < 0 ? (unsigned)-sample : (unsigned)sample;
            audio_zero += magnitude < 64;
            audio_clipped += magnitude >= 32760;
            audio_energy += (uint64_t)magnitude * magnitude;
            if (magnitude > audio_peak) audio_peak = magnitude;
        }
        audio_frames += samples / audio_channels;
    }
    if (audio_callbacks == 50 || audio_callbacks == 150 || audio_callbacks == 300 ||
        audio_callbacks == 600 || audio_callbacks == 900)
        report("audio");
}

int SDL_OpenAudio(SDL_AudioSpec *desired, SDL_AudioSpec *obtained)
{
    static int (*real_open)(SDL_AudioSpec *, SDL_AudioSpec *);
    if (!real_open) real_open = dlsym(RTLD_NEXT, "SDL_OpenAudio");
    if (!real_open || !desired) return -1;
    original_audio = desired->callback;
    original_audio_data = desired->userdata;
    audio_rate = desired->freq;
    audio_channels = desired->channels;
    audio_format = desired->format;
    desired->callback = audio_callback;
    desired->userdata = NULL;
    return real_open(desired, obtained);
}

int SDL_Flip(SDL_Surface *surface)
{
    static int (*real_flip)(SDL_Surface *);
    uint64_t start, elapsed;
    int rc;
    if (!real_flip) real_flip = dlsym(RTLD_NEXT, "SDL_Flip");
    if (!real_flip) return -1;
    start = now_ns();
    if (!flip_first) flip_first = start;
    flip_last = start;
    rc = real_flip(surface);
    elapsed = now_ns() - start;
    flips++;
    flip_wait_ns += elapsed;
    if (elapsed > flip_max_ns) flip_max_ns = elapsed;
    flip_waits_8ms += elapsed >= 8000000ULL;
    if (flips == 60 || flips == 180 || flips == 360 || flips == 600) report("video");
    return rc;
}
