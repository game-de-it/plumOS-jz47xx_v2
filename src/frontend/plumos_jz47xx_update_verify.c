/* Verify and unpack a signed JZ47xx runtime update into a private staging directory. */
#include <ctype.h>
#include <fcntl.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define MAX_BYTES (256UL * 1024 * 1024)
#define MAX_FILES 256

static int verify(FILE *package, const char *key_path) {
  unsigned char signature[512], buffer[32768];
  size_t count, total = 0;
  int length, valid = 0;
  FILE *pem = fopen(key_path, "r");
  EVP_PKEY *key = pem ? PEM_read_PUBKEY(pem, NULL, NULL, NULL) : NULL;
  EVP_MD_CTX *hash = EVP_MD_CTX_new();
  if (pem) fclose(pem);
  if (!key || !hash || EVP_PKEY_base_id(key) != EVP_PKEY_RSA) goto done;
  length = EVP_PKEY_size(key);
  if (length < 256 || length > (int)sizeof(signature) ||
      fread(signature, 1, length, package) != (size_t)length ||
      EVP_DigestVerifyInit(hash, NULL, EVP_sha256(), NULL, key) != 1) goto done;
  while ((count = fread(buffer, 1, sizeof(buffer), package))) {
    total += count;
    if (total > MAX_BYTES || EVP_DigestVerifyUpdate(hash, buffer, count) != 1)
      goto done;
  }
  valid = !ferror(package) &&
          EVP_DigestVerifyFinal(hash, signature, length) == 1 &&
          fseek(package, length, SEEK_SET) == 0;
done:
  EVP_MD_CTX_free(hash);
  EVP_PKEY_free(key);
  return valid;
}

static int allowed_path(const char *path) {
  static const char *const fixed[] = {
    "VERSION", "bin/plumos-controller-ui", "bin/plumos-text-ui",
    "bin/plumos-library-scan",
    "bin/plumos-rg280v-power-menu", "picoarch/bin/picoarch", "bin/pcsx4all",
    "config/frontend/apps.json", "config/frontend/menus.json",
    "config/frontend/systems.json"
  };
  static const struct { const char *dir, *suffix; } groups[] = {
    {"picoarch/cores/", "_libretro.so"}, {"emulators/opk/", ".opk"},
    {"emulators/", ".opk"}
  };
  size_t i;
  for (i = 0; i < sizeof(fixed) / sizeof(fixed[0]); ++i) {
    if (!strcmp(path, fixed[i])) return 1;
  }
  for (i = 0; i < sizeof(groups) / sizeof(groups[0]); ++i) {
    size_t prefix = strlen(groups[i].dir), suffix = strlen(groups[i].suffix);
    if (!strncmp(path, groups[i].dir, prefix)) {
      const char *name = path + prefix;
      size_t length = strlen(name);
      if (length <= suffix || !isalnum((unsigned char)name[0]) ||
          strcmp(name + length - suffix, groups[i].suffix)) continue;
      if (strspn(name, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                      "0123456789._+-") == length) return 1;
    }
  }
  return 0;
}

/* Reject NUL, overlong lines and CR so the binary parser and shell agree. */
static int read_line(FILE *stream, char *line, size_t capacity) {
  size_t used = 0;
  int c;
  while ((c = fgetc(stream)) != '\n') {
    if (c == EOF) return used || ferror(stream) ? -1 : 0;
    if (c == 0 || c == '\r' || used + 1 >= capacity) return -1;
    line[used++] = (char)c;
  }
  line[used] = '\0';
  return 1;
}

static unsigned long read_number(const char *text, unsigned long limit) {
  unsigned long value = 0;
  for (; *text >= '0' && *text <= '9'; ++text) {
    unsigned long digit = (unsigned long)(*text - '0');
    if (value > (limit - digit) / 10) return 0;
    value = value * 10 + digit;
  }
  return *text ? 0 : value;
}

static int unpack(FILE *package) {
  char line[256], name[16], previous[256] = "";
  unsigned char buffer[32768];
  unsigned long revision;
  FILE *list = NULL, *payload = NULL;
  int rc, files = 0, ok = 0;
  if (read_line(package, line, sizeof(line)) != 1 ||
      strcmp(line, "PLUMOS-JZ47XX-RUNTIME-1") ||
      read_line(package, line, sizeof(line)) != 1 ||
      !(revision = read_number(line, 999999999UL))) return 0;

  list = fopen("files", "w");
  if (!list) return 0;
  while ((rc = read_line(package, line, sizeof(line))) == 1) {
    char *separator = strchr(line, '\t');
    unsigned long length;
    int fd;
    if (!separator || files >= MAX_FILES) goto done;
    *separator++ = '\0';
    length = read_number(separator, MAX_BYTES);
    if (!length || !allowed_path(line) || strcmp(line, previous) <= 0) goto done;
    strcpy(previous, line);
    snprintf(name, sizeof(name), "new/%d", ++files);
    fd = open(name, O_CREAT | O_EXCL | O_WRONLY, 0600);
    if (fd < 0) goto done;
    payload = fdopen(fd, "wb");
    if (!payload) { close(fd); goto done; }
    while (length) {
      size_t count = length < sizeof(buffer) ? length : sizeof(buffer);
      if (fread(buffer, 1, count, package) != count ||
          fwrite(buffer, 1, count, payload) != count) goto done;
      length -= count;
    }
    rc = fclose(payload);
    payload = NULL;
    if (rc || fprintf(list, "%s\n", line) < 0) goto done;
  }
  if (rc || !files || ferror(list)) goto done;
  ok = 1;
done:
  if (payload) fclose(payload);
  if (fclose(list)) ok = 0;
  if (ok) {
    FILE *version = fopen("revision", "w");
    if (!version) return 0;
    ok = fprintf(version, "%lu\n", revision) > 0;
    if (fclose(version)) ok = 0;
  }
  return ok;
}

int main(int argc, char **argv) {
  FILE *package;
  int result;
  if (argc != 3) {
    fprintf(stderr, "Usage: %s STAGED_PACKAGE PUBLIC_KEY\n", argv[0]);
    return 2;
  }
  package = fopen(argv[1], "rb");
  if (!package) { perror(argv[1]); return 1; }
  result = verify(package, argv[2]) && unpack(package);
  fclose(package);
  if (!result) fprintf(stderr, "JZ47xx update signature or payload is invalid.\n");
  return result ? 0 : 1;
}
