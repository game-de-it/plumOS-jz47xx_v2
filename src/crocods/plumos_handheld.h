#ifndef CROCODS_PLUMOS_HANDHELD_H
#define CROCODS_PLUMOS_HANDHELD_H

#include <stdint.h>

int plumos_crocods_open(void);
void plumos_crocods_close(void);
const uint8_t *plumos_crocods_keys(void);
int plumos_crocods_present(const uint16_t *pixels, unsigned width, unsigned height);

#endif
