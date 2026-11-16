#!/usr/bin/env python3
"""Keep Lightrec's direct-addressed PSX memory and JIT code at their requested VAs."""

from pathlib import Path
import sys


path = Path(sys.argv[1]) / "libpcsxcore/lightrec/mem.c"
source = path.read_text()
before = "MAP_PRIVATE | /*MAP_FIXED_NOREPLACE |*/ MAP_ANONYMOUS"
after = "MAP_PRIVATE | MAP_FIXED_NOREPLACE | MAP_ANONYMOUS"
if source.count(before) != 4:
    if source.count(after) != 4:
        raise SystemExit("Unexpected Lightrec mmap layout")
else:
    path.write_text(source.replace(before, after))

# The MIPS code emitter can retain an instruction in its delay-slot buffer
# when it restarts a function. The stale instruction is then emitted at the
# entry point before the prologue. This exactly matches the RG280V crash:
# generated code starts with `lw v1,612(v1)` while v1 is zero. Adapted from
# tzubertowski/TreeFrogUI_pcsx_rearmed commit 2f0919a (GPL/LGPL source).
path = Path(sys.argv[1]) / "deps/lightning/lib/jit_mips.c"
source = path.read_text()
before = "\t\t    patch_alist(1);\n\t\t    goto restart_function;"
after = "\t\t    patch_alist(1);\n\t\t    _jitc->inst.pend = 0;\n\t\t    goto restart_function;"
if source.count(before) != 1:
    if source.count(after) != 1:
        raise SystemExit("Unexpected Lightning restart layout")
else:
    path.write_text(source.replace(before, after))
