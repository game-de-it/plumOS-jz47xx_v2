/* RG280V hardware volume and START+LEFT/RIGHT brightness keys. */
#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/wait.h>
#include <unistd.h>

#define SETTINGS "/media/data/plumos/config/system/settings.json"
#define LOCK_FILE "/var/run/plumos-hotkeys.lock"
#define VOLUME_CONTROL "/media/data/plumos/bin/plumos-volume-control"
#define DISPLAY_CONTROL "/media/data/plumos/bin/plumos-display-control"
#define POWER_MENU "/media/data/plumos/bin/plumos-rg280v-power-menu"

static int setting_location(char *json, const char *key, char **value) {
  char pattern[48];
  char *p;
  if (snprintf(pattern, sizeof(pattern), "\"%s\"", key) >= (int)sizeof(pattern)) return 0;
  p = strstr(json, pattern);
  if (!p) return 0;
  p = strchr(p + strlen(pattern), ':');
  if (!p) return 0;
  p++;
  while (*p == ' ' || *p == '\t') p++;
  if (*p < '0' || *p > '9') return 0;
  *value = p;
  return 1;
}

static int read_settings(char *json, size_t capacity) {
  FILE *f = fopen(SETTINGS, "r");
  size_t n;
  if (!f) return 0;
  n = fread(json, 1, capacity - 1, f);
  if (ferror(f) || !feof(f)) { fclose(f); return 0; }
  fclose(f);
  json[n] = '\0';
  return 1;
}

static int run_control(const char *path, int level) {
  char text[12];
  pid_t child;
  int status;
  snprintf(text, sizeof(text), "%d", level);
  child = fork();
  if (child < 0) return 0;
  if (child == 0) {
    execl(path, path, "apply", text, (char *)NULL);
    _exit(127);
  }
  if (waitpid(child, &status, 0) != child) return 0;
  return WIFEXITED(status) && WEXITSTATUS(status) == 0;
}

static void open_power_menu(void) {
  pid_t child = fork();
  int status;
  if (child < 0) return;
  if (child == 0) {
    execl(POWER_MENU, POWER_MENU, (char *)NULL);
    _exit(127);
  }
  (void)waitpid(child, &status, 0);
}

static int adjust(const char *key, int delta, int minimum, int maximum,
                  const char *control) {
  char json[4096], next[4096], *value, *end;
  char temp[sizeof(SETTINGS) + sizeof(".hotkey.tmp")];
  char number[16];
  FILE *f;
  int lockfd, old, target, ok = 0;
  long parsed;
  size_t prefix, suffix, number_len;

  lockfd = open(LOCK_FILE, O_CREAT | O_RDWR, 0600);
  if (lockfd < 0 || flock(lockfd, LOCK_EX) < 0) goto done;
  if (!read_settings(json, sizeof(json)) || !setting_location(json, key, &value)) goto unlock;
  parsed = strtol(value, &end, 10);
  if (parsed < minimum || parsed > maximum || end == value) goto unlock;
  old = (int)parsed;
  target = old + delta;
  if (target < minimum) target = minimum;
  if (target > maximum) target = maximum;
  if (target == old) { ok = 1; goto unlock; }
  snprintf(number, sizeof(number), "%d", target);
  prefix = (size_t)(value - json);
  suffix = strlen(end);
  number_len = strlen(number);
  if (prefix + number_len + suffix + 1 > sizeof(next)) goto unlock;
  memcpy(next, json, prefix);
  memcpy(next + prefix, number, number_len);
  memcpy(next + prefix + number_len, end, suffix + 1);
  if (!run_control(control, target)) goto unlock;
  snprintf(temp, sizeof(temp), "%s.hotkey.tmp", SETTINGS);
  f = fopen(temp, "w");
  if (!f) goto unlock;
  ok = fwrite(next, 1, prefix + number_len + suffix, f) == prefix + number_len + suffix;
  if (ok && (fflush(f) != 0 || fsync(fileno(f)) != 0)) ok = 0;
  if (fclose(f) != 0) ok = 0;
  if (ok) ok = rename(temp, SETTINGS) == 0;
  if (!ok) unlink(temp);
unlock:
  flock(lockfd, LOCK_UN);
done:
  if (lockfd >= 0) close(lockfd);
  return ok;
}

int main(int argc, char **argv) {
  const char *input = argc > 1 ? argv[1] : "/dev/input/event2";
  int fd, start_held = 0;
  struct input_event event;
  struct pollfd pfd;
  while (1) {
    fd = open(input, O_RDONLY | O_CLOEXEC);
    if (fd < 0) { sleep(1); continue; }
    pfd.fd = fd;
    pfd.events = POLLIN;
    while (poll(&pfd, 1, -1) >= 0) {
      if (!(pfd.revents & POLLIN)) break;
      if (read(fd, &event, sizeof(event)) != sizeof(event)) break;
      if (event.type != EV_KEY) continue;
      if (event.code == KEY_ENTER) {
        if (event.value == 0) start_held = 0;
        else if (event.value == 1) start_held = 1;
      } else if (event.value == 1 || event.value == 2) {
        if (event.code == KEY_VOLUMEUP)
          adjust("volume", 1, 0, 20, VOLUME_CONTROL);
        else if (event.code == KEY_VOLUMEDOWN)
          adjust("volume", -1, 0, 20, VOLUME_CONTROL);
        else if (start_held && event.code == KEY_RIGHT)
          adjust("brightness", 1, 1, 6, DISPLAY_CONTROL);
        else if (start_held && event.code == KEY_LEFT)
          adjust("brightness", -1, 1, 6, DISPLAY_CONTROL);
        else if (event.code == KEY_POWER && event.value == 1)
          open_power_menu();
      }
    }
    close(fd);
    start_held = 0;
    sleep(1);
  }
}
