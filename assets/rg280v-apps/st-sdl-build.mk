VERSION = 0.3
PREFIX = /usr
MANPREFIX = /usr/share/man
INCS = -I. -I/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL -D_GNU_SOURCE=1 -D_REENTRANT
LIBS = -lutil -L/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr/lib -lSDL -lpthread -lm
CPPFLAGS = -DVERSION=\"${VERSION}\" -fPIC
CFLAGS = -Os -Wall ${INCS} ${CPPFLAGS} -DRS97 -DPLUMOS_RG280V -msoft-float -fcommon -std=gnu11
LDFLAGS = -msoft-float ${LIBS}
CC = /workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-gcc
