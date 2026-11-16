#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int send_event(int fd, unsigned short type, unsigned short code, int value)
{
    struct input_event event;
    memset(&event, 0, sizeof(event));
    event.type = type;
    event.code = code;
    event.value = value;
    return write(fd, &event, sizeof(event)) == sizeof(event) ? 0 : -1;
}

int main(int argc, char **argv)
{
    char *end;
    long code;
    long duration_ms, second_code = -1;
    int fd;

    if (argc != 4 && argc != 5) {
        fprintf(stderr, "usage: %s /dev/input/eventN keycode duration_ms [second_keycode]\n", argv[0]);
        return 2;
    }
    code = strtol(argv[2], &end, 10);
    if (*end || code < 0 || code > KEY_MAX) return 2;
    duration_ms = strtol(argv[3], &end, 10);
    if (*end || duration_ms < 1 || duration_ms > 5000) return 2;
    if (argc == 5) {
        second_code = strtol(argv[4], &end, 10);
        if (*end || second_code < 0 || second_code > KEY_MAX) return 2;
    }
    fd = open(argv[1], O_WRONLY);
    if (fd < 0) { perror("open"); return 1; }
    if (send_event(fd, EV_KEY, (unsigned short)code, 1) ||
        (second_code >= 0 && send_event(fd, EV_KEY, (unsigned short)second_code, 1)) ||
        send_event(fd, EV_SYN, SYN_REPORT, 0)) {
        perror("press"); close(fd); return 1;
    }
    usleep((useconds_t)duration_ms * 1000);
    if (send_event(fd, EV_KEY, (unsigned short)code, 0) ||
        (second_code >= 0 && send_event(fd, EV_KEY, (unsigned short)second_code, 0)) ||
        send_event(fd, EV_SYN, SYN_REPORT, 0)) {
        perror("release"); close(fd); return 1;
    }
    close(fd);
    return 0;
}
