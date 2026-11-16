/* Initialize the RG280V RTC for a timed suspend diagnostic. */
#include <errno.h>
#include <fcntl.h>
#include <linux/rtc.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>

int main(int argc, char **argv) {
  char *end;
  long epoch;
  time_t seconds;
  struct tm utc;
  struct rtc_time rtc;
  int fd;

  if (argc != 2) {
    fprintf(stderr, "usage: %s <UTC epoch seconds>\n", argv[0]);
    return 2;
  }
  errno = 0;
  epoch = strtol(argv[1], &end, 10);
  if (errno || *end || end == argv[1] || epoch < 946684800L) return 2;
  seconds = (time_t)epoch;
  if ((long)seconds != epoch || !gmtime_r(&seconds, &utc)) return 2;
  rtc.tm_sec = utc.tm_sec;
  rtc.tm_min = utc.tm_min;
  rtc.tm_hour = utc.tm_hour;
  rtc.tm_mday = utc.tm_mday;
  rtc.tm_mon = utc.tm_mon;
  rtc.tm_year = utc.tm_year;
  rtc.tm_wday = utc.tm_wday;
  rtc.tm_yday = utc.tm_yday;
  rtc.tm_isdst = 0;
  fd = open("/dev/rtc0", O_RDWR);
  if (fd < 0) { perror("open rtc0"); return 1; }
  if (ioctl(fd, RTC_SET_TIME, &rtc) < 0) {
    perror("RTC_SET_TIME");
    close(fd);
    return 1;
  }
  close(fd);
  return 0;
}
