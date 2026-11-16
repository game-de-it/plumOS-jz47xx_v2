TARGET=gcw0
CC=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-gcc
STRIP=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-strip
SDL_CFLAGS=-I/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL -D_GNU_SOURCE=1 -D_REENTRANT
SDL_LIB=-lSDL
COPTS=-O2 -msoft-float
CFLAGS=$(SDL_CFLAGS) -msoft-float -fcommon -fsigned-char -D_REENTRANT -DUSE_MEMORY_H -DPLUMOS_RG280V -DSDLFE_NO_HWACCEL
LFLAGS=-msoft-float -L/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr/lib -Wl,-export-dynamic -lm -ldl -lz
LFLAGS_CORE=
LIBS_CORE=-lpthread
DECODERS_TO_BUILD=decoders/mpg123.so decoders/vorbis.so decoders/flac.so
FRONTENDS_TO_BUILD=frontends/sdl.so
TOOLS_TO_BUILD=gmu.bin
