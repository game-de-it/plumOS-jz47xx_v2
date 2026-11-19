#!/usr/bin/env bash
# Exercise the actual preload source against a small fake SDL backend.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
docker run --rm --platform linux/arm64 \
    -v "$repo:/workspace:ro" -v plumos-jz47xx-rg280v-build:/sdk:ro \
    plumos-jz47xx-build:bookworm bash -euc '
stage=$(mktemp -d)
trap '\''rm -rf "$stage"'\'' EXIT
cp -a /sdk/host/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL "$stage/SDL"
include="$stage/SDL"
cat >"$stage/backend.c" <<'\''C'\''
#include <SDL.h>
#include <string.h>
int backend_result;
char backend_name[32] = "kmsdrm";
SDL_VideoInfo backend_info;
SDL_Rect backend_panel;
SDL_Rect *backend_modes[] = { &backend_panel, 0 };
int SDL_VideoModeOK(int w, int h, int bpp, Uint32 flags) { return backend_result; }
char *SDL_VideoDriverName(char *name, int max) {
    if (!backend_name[0]) return 0;
    strncpy(name, backend_name, max); name[max-1]=0; return name;
}
const SDL_VideoInfo *SDL_GetVideoInfo(void) { return &backend_info; }
SDL_Rect **SDL_ListModes(SDL_PixelFormat *format, Uint32 flags) { return backend_modes; }
C
cat >"$stage/check.c" <<'\''C'\''
#include <SDL.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
extern int backend_result;
extern char backend_name[32];
extern SDL_VideoInfo backend_info;
extern SDL_Rect backend_panel;
int main(void) {
    const int modes[][2]={{320,240},{280,240},{256,240},{256,224},{240,240},{240,224}};
    const int panels[][2]={{640,480},{320,480},{320,240}};
    backend_info.current_w=640; backend_info.current_h=480;
    backend_panel.w=640; backend_panel.h=480;
    unsetenv("PLUMOS_FCEUX_LEGACY_MODE_CHECK");
    assert(SDL_VideoModeOK(320,240,16,0)==0);
    setenv("PLUMOS_FCEUX_LEGACY_MODE_CHECK","0",1);
    assert(SDL_VideoModeOK(320,240,16,0)==0);
    setenv("PLUMOS_FCEUX_LEGACY_MODE_CHECK","1",1);
    for (unsigned p=0;p<3;p++) {
        backend_info.current_w=panels[p][0]; backend_info.current_h=panels[p][1];
        backend_panel.w=panels[p][0]; backend_panel.h=panels[p][1];
        for (unsigned m=0;m<6;m++)
            assert(SDL_VideoModeOK(modes[m][0],modes[m][1],16,0x40000101)==16);
    }
    assert(SDL_VideoModeOK(640,480,16,0)==0);
    assert(SDL_VideoModeOK(319,239,16,0)==0);
    assert(SDL_VideoModeOK(320,240,8,0)==0);
    assert(SDL_VideoModeOK(320,240,32,0)==0);
    assert(SDL_VideoModeOK(0,240,16,0)==0);
    backend_panel.w=160;
    assert(SDL_VideoModeOK(320,240,16,0)==0);
    backend_panel.w=640; backend_panel.h=480;
    backend_info.current_w=240; backend_info.current_h=224;
    assert(SDL_VideoModeOK(320,240,16,0)==16);
    backend_info.current_w=640; backend_info.current_h=480;
    strcpy(backend_name,"fbcon");
    assert(SDL_VideoModeOK(320,240,16,0)==0);
    backend_name[0]=0;
    assert(SDL_VideoModeOK(320,240,16,0)==0);
    strcpy(backend_name,"kmsdrm"); backend_result=32;
    assert(SDL_VideoModeOK(320,240,16,0)==32);
    unsetenv("PLUMOS_FCEUX_LEGACY_MODE_CHECK");
    assert(SDL_VideoModeOK(320,240,16,0)==32);
    puts("legacy mode guards: passed (18 panel/mode pairs and negative cases)");
    return 0;
}
C
cc -fPIC -shared -I"$include" "$stage/backend.c" -o "$stage/libbackend.so"
cc -fPIC -shared -Wall -Wextra -I"$include" -I"$(dirname "$include")" \
    /workspace/scripts/rg280v-fceux-menu.c -o "$stage/libcheck.so" -ldl
cc -I"$include" "$stage/check.c" -L"$stage" -Wl,-rpath,"$stage" \
    -lcheck -lbackend -o "$stage/check"
"$stage/check"
'
