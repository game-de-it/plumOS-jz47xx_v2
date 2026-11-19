#define _FILE_OFFSET_BITS 64

#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <linux/blkpg.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <unistd.h>

static long long sector_bytes(const char *text)
{
    char *end;
    long long sectors;

    errno = 0;
    sectors = strtoll(text, &end, 10);
    if (errno || end == text || *end != '\0' || sectors <= 0 ||
        sectors > LLONG_MAX / 512) {
        fprintf(stderr, "Invalid sector count: %s\n", text);
        exit(2);
    }
    return sectors * 512;
}

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "Usage: %s DEVICE START_SECTOR SECTOR_COUNT\n", argv[0]);
        return 2;
    }

    struct blkpg_partition partition = {
        .pno = 3,
        .start = sector_bytes(argv[2]),
        .length = sector_bytes(argv[3]),
    };
    struct blkpg_ioctl_arg operation = {
        .op = BLKPG_RESIZE_PARTITION,
        .datalen = sizeof(partition),
        .data = &partition,
    };

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror(argv[1]);
        return 1;
    }
    int result = ioctl(fd, BLKPG, &operation);
    if (result < 0)
        perror("BLKPG_RESIZE_PARTITION p3");
    close(fd);
    return result < 0;
}
