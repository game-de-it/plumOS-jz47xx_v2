/* Run an OPK in its own process group and terminate the whole group on timeout. */
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static double monotonic_seconds(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1000000000.0;
}

int main(int argc, char **argv)
{
    pid_t child;
    char **opk_argv;
    int status;
    double deadline;
    struct timespec pause_time = {0, 100000000};
    char *end;
    long seconds;
    if (argc < 3) {
        fprintf(stderr, "usage: %s SECONDS OPK [ROM]\n", argv[0]);
        return 2;
    }
    seconds = strtol(argv[1], &end, 10);
    if (*end || seconds < 1 || seconds > 300) return 2;
    opk_argv = calloc((size_t)argc, sizeof(*opk_argv));
    if (!opk_argv) { perror("calloc"); return 1; }
    opk_argv[0] = "/usr/bin/opkrun";
    for (int i = 2; i < argc; ++i) opk_argv[i - 1] = argv[i];
    child = fork();
    if (child < 0) { perror("fork"); return 1; }
    if (child == 0) {
        if (setsid() < 0) { perror("setsid"); _exit(1); }
        execv("/usr/bin/opkrun", opk_argv);
        perror("execv opkrun");
        _exit(127);
    }
    deadline = monotonic_seconds() + seconds;
    while (monotonic_seconds() < deadline) {
        pid_t result = waitpid(child, &status, WNOHANG);
        if (result == child) {
            if (WIFEXITED(status)) return WEXITSTATUS(status);
            if (WIFSIGNALED(status)) return 128 + WTERMSIG(status);
            return 1;
        }
        if (result < 0 && errno != EINTR) { perror("waitpid"); return 1; }
        nanosleep(&pause_time, NULL);
    }
    kill(-child, SIGTERM);
    nanosleep(&pause_time, NULL);
    kill(-child, SIGKILL);
    waitpid(child, &status, 0);
    fprintf(stderr, "watchdog: timeout after %ld s\n", seconds);
    return 124;
}
