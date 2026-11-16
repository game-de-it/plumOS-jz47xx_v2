/* Low-overhead MIPS PC sampling for a short RG280V profiling run.
 * Set PLUMOS_PC_SAMPLE_FILE, preload this library, then send SIGUSR1 to dump.
 * The output is a sequence of little-endian uint32_t program counters.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/ucontext.h>
#include <fcntl.h>
#include <unistd.h>

#if !defined(__mips__) || __SIZEOF_POINTER__ != 4
#error This sampler requires 32-bit MIPS
#endif

#define SAMPLE_CAPACITY 60000
static uint32_t samples[SAMPLE_CAPACITY];
static volatile sig_atomic_t sample_count;
static int sample_fd = -1;

static void sample_pc(int signo, siginfo_t *info, void *context)
{
    ucontext_t *uc = (ucontext_t *)context;
    sig_atomic_t n = sample_count;
    (void)signo;
    (void)info;
    if (n < SAMPLE_CAPACITY) {
        samples[n] = (uint32_t)uc->uc_mcontext.pc;
        sample_count = n + 1;
    }
}

static void dump_samples(int signo)
{
    sig_atomic_t n = sample_count;
    size_t left = (size_t)n * sizeof(samples[0]);
    const char *ptr = (const char *)samples;
    (void)signo;
    while (left && sample_fd >= 0) {
        ssize_t written = write(sample_fd, ptr, left);
        if (written > 0) {
            ptr += written;
            left -= (size_t)written;
        } else if (written < 0 && errno == EINTR) {
            continue;
        } else {
            break;
        }
    }
    sample_count = 0;
}

static void finish_sampling(void)
{
    struct itimerval off = {0};
    setitimer(ITIMER_PROF, &off, NULL);
    dump_samples(0);
    if (sample_fd >= 0)
        close(sample_fd);
}

__attribute__((constructor)) static void start_sampling(void)
{
    const char *path = getenv("PLUMOS_PC_SAMPLE_FILE");
    struct sigaction sa = {0};
    struct itimerval timer = {0};
    if (!path || !*path)
        return;
    sample_fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (sample_fd < 0)
        return;

    sa.sa_sigaction = sample_pc;
    sa.sa_flags = SA_SIGINFO | SA_RESTART;
    sigemptyset(&sa.sa_mask);
    sigaddset(&sa.sa_mask, SIGUSR1);
    if (sigaction(SIGPROF, &sa, NULL) < 0)
        goto fail;

    sa.sa_handler = dump_samples;
    sa.sa_flags = SA_RESTART;
    sigemptyset(&sa.sa_mask);
    sigaddset(&sa.sa_mask, SIGPROF);
    if (sigaction(SIGUSR1, &sa, NULL) < 0)
        goto fail;

    timer.it_value.tv_usec = 1000;
    timer.it_interval.tv_usec = 1000;
    if (setitimer(ITIMER_PROF, &timer, NULL) < 0)
        goto fail;
    atexit(finish_sampling);
    return;
fail:
    close(sample_fd);
    sample_fd = -1;
}
