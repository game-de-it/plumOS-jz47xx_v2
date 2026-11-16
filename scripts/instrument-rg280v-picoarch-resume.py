#!/usr/bin/env python3
"""Allow a one-time RG280V comparison build to load save-state slot 0."""

from pathlib import Path
import sys

path = Path(sys.argv[1]) / "main.c"
source = path.read_text()
before = "\tstate_resume();\n\n\tdo {"
after = '''\tstate_resume();
    /* Diagnostic-only: load the same saved race in each PSX core. */
    const char *plumos_resume = getenv("PLUMOS_PICOARCH_RESUME_SLOT");
    if (plumos_resume && strcmp(plumos_resume, "0") == 0) {
        state_slot = 0;
        if (state_read() != 0)
            PA_ERROR("PLUMOS_PICOARCH_RESUME_SLOT=0 failed\\n");
        else
            PA_INFO("PLUMOS_PICOARCH_RESUME_SLOT=0 loaded\\n");
    }

\tdo {'''
if source.count(before) != 1:
    raise SystemExit("unexpected PicoArch state resume code")
source = source.replace(before, after, 1)
if "#include <stdlib.h>" not in source:
    source = source.replace("#include <stdio.h>\n", "#include <stdio.h>\n#include <stdlib.h>\n", 1)
path.write_text(source)
