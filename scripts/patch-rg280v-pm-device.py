#!/usr/bin/env python3
"""Record the last noirq device name hash in the RG280V RTC scratchpad."""

from pathlib import Path
import sys

kernel = Path(sys.argv[1])
main = Path(sys.argv[2])
s = kernel.read_text()
old = 'writel(0x504d0000 | stage, rtc + 0x34);'
if s.count(old) == 1:
    kernel.write_text(s.replace(old, 'writel(stage >= 0x10000 ? stage : 0x504d0000 | stage, rtc + 0x34);'))

s = main.read_text()
anchor = 'static int dpm_noirq_suspend_devices(pm_message_t state)\n'
helper = '''static u32 rg280v_pm_device_hash(const char *name)
{
\tu32 hash = 5381;

\twhile (*name)
\t\thash = hash * 33 + (u8)*name++;
\treturn hash & 0xffffff;
}

'''
assert s.count(anchor) == 1
s = s.replace(anchor, 'extern void rg280v_pm_mark(u32 stage);\n\n' + helper + anchor)
old = '\t\terror = device_suspend_noirq(dev);'
assert s.count(old) == 1
s = s.replace(old, '\t\trg280v_pm_mark(0x51000000 | rg280v_pm_device_hash(dev_name(dev)));\n' + old + '\n\t\trg280v_pm_mark(0x52000000 | rg280v_pm_device_hash(dev_name(dev)));')
main.write_text(s)
