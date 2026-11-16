#!/usr/bin/env python3
"""Add temporary RTC markers around Linux's noirq suspend steps."""

from pathlib import Path
import sys

kernel = Path(sys.argv[1])
main = Path(sys.argv[2])
s = kernel.read_text()
old = 'static void rg280v_pm_mark(u32 stage)'
assert s.count(old) == 1
kernel.write_text(s.replace(old, 'void rg280v_pm_mark(u32 stage)'))

s = main.read_text()
assert 'rg280v_pm_mark(' not in s
anchor = 'int dpm_suspend_noirq(pm_message_t state)\n'
assert s.count(anchor) == 1
s = s.replace(anchor, 'extern void rg280v_pm_mark(u32 stage);\n\n' + anchor)
for old, new in [
    ('\tdevice_wakeup_arm_wake_irqs();', '\trg280v_pm_mark(11);\n\tdevice_wakeup_arm_wake_irqs();\n\trg280v_pm_mark(12);'),
    ('\tsuspend_device_irqs();', '\tsuspend_device_irqs();\n\trg280v_pm_mark(13);'),
    ('\tret = dpm_noirq_suspend_devices(state);', '\tret = dpm_noirq_suspend_devices(state);\n\trg280v_pm_mark(14);'),
]:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
main.write_text(s)
