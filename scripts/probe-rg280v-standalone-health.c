/* RG280V SDL 1.2 standalone video and audio telemetry. */
#define _GNU_SOURCE
#include <SDL/SDL.h>
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

static void (*original_audio)(void *, Uint8 *, int);
static void *original_audio_data;
static unsigned audio_callbacks;
static uint64_t audio_frames, audio_zero, audio_clipped, audio_energy;
static unsigned audio_peak;
static int audio_min = 32767, audio_max = -32768;
static unsigned audio_rate, audio_channels, audio_format;
static uint64_t audio_first, audio_last;
static unsigned flips;
static __thread int presenting;
static uint64_t flip_first, flip_last, flip_wait_ns, flip_max_ns;
static unsigned flip_waits_8ms;
static unsigned flip_report_count;
static uint64_t flip_report_time;
static uint64_t input_first;
static unsigned autostart_ms;
static unsigned autostart_count;
static unsigned autostart_pulses;
static SDLKey autostart_key;
static int autostart_init, autostart_down;

static uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

static void report(const char *kind)
{
    const char *path = getenv("PLUMOS_STANDALONE_HEALTH_LOG");
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
        fprintf(out, "audio\tcallbacks=%u\trate=%u\tchannels=%u\tformat=0x%x\tframes=%llu\tseconds=%.3f\tzero_frac=%.4f\tclipped_frac=%.4f\tpeak=%u\tenergy=%llu\tmin=%d\tmax=%d\n",
                audio_callbacks, audio_rate, audio_channels, audio_format,
                (unsigned long long)audio_frames,
                audio_last > audio_first ? (double)(audio_last - audio_first) / 1e9 : 0.0,
                audio_frames ? (double)audio_zero / (audio_frames * audio_channels) : 0.0,
                audio_frames ? (double)audio_clipped / (audio_frames * audio_channels) : 0.0,
                audio_peak, (unsigned long long)audio_energy, audio_min, audio_max);
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
    (void)ignored;
    if (original_audio) original_audio(original_audio_data, stream, len);
    audio_last = now_ns();
    if (!audio_first) audio_first = audio_last;
    audio_callbacks++;
    if (audio_channels && ((audio_format & 0xff) == 16 || (audio_format & 0xff) == 8)) {
        unsigned width = (audio_format & 0xff) / 8;
        samples = (unsigned)len / width;
        for (i = 0; i < samples; i++) {
            int sample;
            if (width == 1) {
                sample = (audio_format & 0x8000) ? (int)(int8_t)stream[i] : (int)stream[i] - 128;
                sample *= 256;
            } else {
                unsigned lo = stream[2*i], hi = stream[2*i+1];
                unsigned raw = (audio_format & 0x1000) ? (lo << 8) | hi : (hi << 8) | lo;
                sample = (audio_format & 0x8000) ? (int)(int16_t)raw : (int)raw - 32768;
            }
            if (sample < audio_min) audio_min = sample;
            if (sample > audio_max) audio_max = sample;
            unsigned magnitude = sample < 0 ? (unsigned)-sample : (unsigned)sample;
            audio_zero += magnitude < 64;
            audio_clipped += magnitude >= 32760;
            audio_energy += (uint64_t)magnitude * magnitude;
            if (magnitude > audio_peak) audio_peak = magnitude;
        }
        audio_frames += samples / audio_channels;
    }
    if (audio_callbacks == 50 || audio_callbacks == 150 || audio_callbacks == 300 ||
        audio_callbacks == 600 || audio_callbacks == 900 ||
        (audio_callbacks > 900 && audio_callbacks % 300 == 0))
        report("audio");
}

int SDL_OpenAudio(SDL_AudioSpec *desired, SDL_AudioSpec *obtained)
{
    static int (*real_open)(SDL_AudioSpec *, SDL_AudioSpec *);
    int rc;
    if (!real_open) real_open = dlsym(RTLD_NEXT, "SDL_OpenAudio");
    if (!real_open || !desired) return -1;
    original_audio = desired->callback;
    original_audio_data = desired->userdata;
    audio_rate = desired->freq;
    audio_channels = desired->channels;
    audio_format = desired->format;
    desired->callback = audio_callback;
    desired->userdata = NULL;
    rc = real_open(desired, obtained);
    if (rc == 0 && obtained) {
        audio_rate = obtained->freq;
        audio_channels = obtained->channels;
        audio_format = obtained->format;
    }
    return rc;
}

static void record_video(uint64_t start, uint64_t elapsed)
{
    if (!flip_first) flip_first = start;
    flip_last = start;
    flips++;
    flip_wait_ns += elapsed;
    if (elapsed > flip_max_ns) flip_max_ns = elapsed;
    flip_waits_8ms += elapsed >= 8000000ULL;
    if (flips == 30 || flips == 60 || flips == 120 || flips == 240 ||
        flips == 480 || flips == 960 ||
        (flips > 960 && flips % 240 == 0)) report("video");
}

int SDL_Flip(SDL_Surface *surface)
{
    static int (*real_flip)(SDL_Surface *);
    uint64_t start, elapsed;
    int rc, nested;
    if (!real_flip) real_flip = dlsym(RTLD_NEXT, "SDL_Flip");
    if (!real_flip) return -1;
    start = now_ns();
    nested = presenting++;
    rc = real_flip(surface);
    presenting--;
    elapsed = now_ns() - start;
    if (!nested) record_video(start, elapsed);
    return rc;
}

int SDL_DisplayYUVOverlay(SDL_Overlay *overlay, SDL_Rect *dstrect)
{
    static int (*real_display)(SDL_Overlay *, SDL_Rect *);
    uint64_t start;
    int rc, nested;
    if (!real_display) real_display = dlsym(RTLD_NEXT, "SDL_DisplayYUVOverlay");
    if (!real_display) return -1;
    start = now_ns();
    nested = presenting++;
    rc = real_display(overlay, dstrect);
    presenting--;
    if (!nested) record_video(start, now_ns() - start);
    return rc;
}


/* SDL2 frontends and SDL1 software surfaces do not necessarily call SDL_Flip. */
void SDL_GL_SwapWindow(void *window)
{
    static void (*real_swap)(void *);
    if (!real_swap) real_swap = dlsym(RTLD_NEXT, "SDL_GL_SwapWindow");
    if (!real_swap) return;
    uint64_t start = now_ns();
    int nested = presenting++;
    real_swap(window);
    presenting--;
    if (!nested) record_video(start, now_ns() - start);
}

void SDL_RenderPresent(void *renderer)
{
    static void (*real_present)(void *);
    if (!real_present) real_present = dlsym(RTLD_NEXT, "SDL_RenderPresent");
    if (!real_present) return;
    uint64_t start = now_ns();
    int nested = presenting++;
    real_present(renderer);
    presenting--;
    if (!nested) record_video(start, now_ns() - start);
}

void SDL_UpdateRects(SDL_Surface *surface, int count, SDL_Rect *rects)
{
    static void (*real_update)(SDL_Surface *, int, SDL_Rect *);
    if (!real_update) real_update = dlsym(RTLD_NEXT, "SDL_UpdateRects");
    if (!real_update) return;
    int nested = presenting++;
    uint64_t start = now_ns();
    real_update(surface, count, rects);
    presenting--;
    if (!nested) record_video(start, now_ns() - start);
}

static void init_autostart(void)
{
    const char *value, *key, *pulses;
    if (autostart_init) return;
    value = getenv("PLUMOS_STANDALONE_AUTOSTART_MS");
    key = getenv("PLUMOS_STANDALONE_AUTOSTART_KEY");
    pulses = getenv("PLUMOS_STANDALONE_AUTOSTART_PULSES");
    autostart_ms = value ? (unsigned)strtoul(value, NULL, 10) : 0;
    autostart_key = key ? (SDLKey)strtoul(key, NULL, 10) : SDLK_RETURN;
    autostart_pulses = pulses ? (unsigned)strtoul(pulses, NULL, 10) : 5;
    if (autostart_pulses > 20) autostart_pulses = 20;
    input_first = now_ns();
    autostart_init = 1;
}

static int synthetic_key(SDL_Event *event)
{
    uint64_t elapsed_ms;
    init_autostart();
    if (!autostart_ms) return 0;
    elapsed_ms = (now_ns() - input_first) / 1000000ULL;
    if (!autostart_down && autostart_count < autostart_pulses &&
        elapsed_ms >= autostart_ms + autostart_count * 4000U) {
        const char *path = getenv("PLUMOS_STANDALONE_HEALTH_LOG");
        FILE *out = path ? fopen(path, "a") : NULL;
        if (out) { fprintf(out, "input\tstart_down_ms=%llu\tpulse=%u\n",
                            (unsigned long long)elapsed_ms, autostart_count + 1); fclose(out); }
        memset(event, 0, sizeof(*event));
        event->type = SDL_KEYDOWN;
        event->key.state = SDL_PRESSED;
        event->key.keysym.sym = autostart_key;
        autostart_down = 1;
        return 1;
    } else if (autostart_down &&
               elapsed_ms >= autostart_ms + autostart_count * 4000U + 250) {
        const char *path = getenv("PLUMOS_STANDALONE_HEALTH_LOG");
        FILE *out = path ? fopen(path, "a") : NULL;
        if (out) { fprintf(out, "input\tstart_up_ms=%llu\tpulse=%u\n",
                            (unsigned long long)elapsed_ms, autostart_count + 1); fclose(out); }
        memset(event, 0, sizeof(*event));
        event->type = SDL_KEYUP;
        event->key.state = SDL_RELEASED;
        event->key.keysym.sym = autostart_key;
        autostart_count++;
        autostart_down = 0;
        return 1;
    }
    return 0;
}

Uint8 *SDL_GetKeyState(int *numkeys)
{
    static Uint8 *(*real_get)(int *);
    Uint8 *state;
    int count = 0;
    uint64_t elapsed_ms;
    if (!real_get) real_get = dlsym(RTLD_NEXT, "SDL_GetKeyState");
    if (!real_get) return NULL;
    state = real_get(&count);
    if (numkeys) *numkeys = count;
    init_autostart();
    if (!state || !autostart_ms || autostart_key < 0 || (int)autostart_key >= count)
        return state;
    elapsed_ms = (now_ns() - input_first) / 1000000ULL;
    if (elapsed_ms >= autostart_ms &&
        elapsed_ms < autostart_ms + autostart_pulses * 4000U)
        state[autostart_key] = ((elapsed_ms - autostart_ms) % 4000U) < 500;
    else if (elapsed_ms >= autostart_ms + autostart_pulses * 4000U)
        state[autostart_key] = 0;
    return state;
}

int SDL_PeepEvents(SDL_Event *events, int numevents, SDL_eventaction action,
                   Uint32 mask)
{
    static int (*real_peep)(SDL_Event *, int, SDL_eventaction, Uint32);
    int count;
    if (!real_peep) real_peep = dlsym(RTLD_NEXT, "SDL_PeepEvents");
    if (!real_peep) return -1;
    count = real_peep(events, numevents, action, mask);
    if (count < 0 || action != SDL_PEEKEVENT || numevents < 1 ||
        count >= numevents || !events)
        return count;
    if (synthetic_key(&events[count])) return count + 1;
    return count;
}

int SDL_PollEvent(SDL_Event *event)
{
    static int (*real_poll)(SDL_Event *);
    int count;
    if (!real_poll) real_poll = dlsym(RTLD_NEXT, "SDL_PollEvent");
    if (!real_poll) return 0;
    count = real_poll(event);
    if (count || !event) return count;
    return synthetic_key(event);
}
