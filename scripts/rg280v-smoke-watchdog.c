/* Kill a game process group after a bounded unattended smoke test. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static double seconds_now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

int main(int argc, char **argv)
{
    pid_t child;
    int status, duration;
    double deadline, term_deadline = 0;
    int phase = 0;
    struct timespec interval = {0, 100000000};

    if (argc < 4 || (duration = atoi(argv[1])) < 2 || duration > 120) return 2;
    child = fork();
    if (child < 0) return 3;
    if (!child) {
        setsid();
        execvp(argv[2], argv + 2);
        perror("execvp");
        _exit(127);
    }
    deadline = seconds_now() + duration;
    for (;;) {
        pid_t waited = waitpid(child, &status, WNOHANG);
        if (waited == child) {
            if (phase) {
                puts("watchdog: timeout");
                return 124;
            }
            if (WIFEXITED(status)) {
                printf("watchdog: exit=%d\n", WEXITSTATUS(status));
                return WEXITSTATUS(status);
            }
            printf("watchdog: signal=%d\n", WTERMSIG(status));
            return 128 + WTERMSIG(status);
        }
        if (waited < 0 && errno != EINTR) return 3;
        if (!phase && seconds_now() >= deadline) {
            kill(-child, SIGTERM);
            phase = 1;
            term_deadline = seconds_now() + 2;
        } else if (phase == 1 && seconds_now() >= term_deadline) {
            kill(-child, SIGKILL);
            phase = 2;
            term_deadline = seconds_now() + 2;
        } else if (phase == 2 && seconds_now() >= term_deadline) {
            puts("watchdog: process remained after SIGKILL");
            return 125;
        }
        nanosleep(&interval, NULL);
    }
}
