#!/usr/bin/env python3
"""Add temporary per-stage frame timing to a patched PicoArch checkout."""

from pathlib import Path
import sys

main = Path(sys.argv[1]) / "main.c"
source = main.read_text()


def replace_once(before: str, after: str) -> None:
    global source
    if source.count(before) != 1:
        raise SystemExit(f"unexpected PicoArch main.c near {before[:50]!r}")
    source = source.replace(before, after, 1)


replace_once(
    "#include <unistd.h>\n",
    "#include <unistd.h>\n#include <stdlib.h>\n#include <sys/time.h>\n",
)
replace_once(
    "\tstate_resume();\n\n\tdo {\n\t\tcount_fps();\n\t\tadjust_audio();\n\t\tcurrent_core.retro_run();\n\t\tif (!should_quit)\n\t\t\tplat_video_flip();\n\t} while (!should_quit);",
    '''\tstate_resume();

    const char *timing_path = getenv("PLUMOS_PICOARCH_TIMING_LOG");
    FILE *timing_log = timing_path ? fopen(timing_path, "w") : NULL;
    unsigned timing_frames = 0;
    unsigned long long timing_audio_us = 0;
    unsigned long long timing_run_us = 0;
    unsigned long long timing_flip_us = 0;
    struct timeval t0, t1, t2, t3, t_batch;

\tdo {
\t\tcount_fps();
        if (timing_log) {
            gettimeofday(&t0, NULL);
            if (timing_frames == 0) t_batch = t0;
        }
\t\tadjust_audio();
        if (timing_log) gettimeofday(&t1, NULL);
\t\tcurrent_core.retro_run();
        if (timing_log) gettimeofday(&t2, NULL);
\t\tif (!should_quit)
\t\t\tplat_video_flip();
        if (timing_log) {
            gettimeofday(&t3, NULL);
            timing_audio_us += (t1.tv_sec - t0.tv_sec) * 1000000ULL + t1.tv_usec - t0.tv_usec;
            timing_run_us += (t2.tv_sec - t1.tv_sec) * 1000000ULL + t2.tv_usec - t1.tv_usec;
            timing_flip_us += (t3.tv_sec - t2.tv_sec) * 1000000ULL + t3.tv_usec - t2.tv_usec;
            if (++timing_frames == 120) {
                unsigned long long wall_us =
                    (t3.tv_sec - t_batch.tv_sec) * 1000000ULL + t3.tv_usec - t_batch.tv_usec;
                fprintf(timing_log, "frames=120\\twall_us=%llu\\taudio_us=%llu\\trun_us=%llu\\tflip_us=%llu\\n",
                        wall_us / 120, timing_audio_us / 120,
                        timing_run_us / 120, timing_flip_us / 120);
                fflush(timing_log);
                timing_frames = 0;
                timing_audio_us = timing_run_us = timing_flip_us = 0;
            }
        }
\t} while (!should_quit);
    if (timing_log) fclose(timing_log);''',
)
main.write_text(source)
