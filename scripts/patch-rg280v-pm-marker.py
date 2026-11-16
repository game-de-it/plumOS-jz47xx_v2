#!/usr/bin/env python3
"""Temporarily mark suspend stages in the RG280V RTC scratchpad.

Diagnostic only: the marker invalidates RTC time until it is set again.
"""

from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text()
if "rg280v_pm_mark(" in source:
    raise SystemExit("marker already installed")

source = source.replace('#include <linux/io.h>', '#include <linux/io.h>\n#include <linux/iopoll.h>')
anchor = 'static int suspend_enter(suspend_state_t state, bool *wakeup)\n'
helper = '''/* RG280V diagnostic: RTC scratchpad survives the hardware RESET. */
static void rg280v_pm_mark(u32 stage)
{
\tvoid __iomem *rtc = ioremap(0x10003000, 0x40);
\tu32 value;

\tif (!rtc)
\t\treturn;
\tif (!readl_poll_timeout_atomic(rtc, value, value & BIT(7), 1, 1000)) {
\t\twritel(0xa55a, rtc + 0x3c);
\t\tif (!readl_poll_timeout_atomic(rtc + 0x3c, value,
\t\t\t\t\t       value & BIT(31), 1, 1000) &&
\t\t    !readl_poll_timeout_atomic(rtc, value,
\t\t\t\t\t       value & BIT(7), 1, 1000))
\t\t\twritel(0x504d0000 | stage, rtc + 0x34);
\t}
\tiounmap(rtc);
}

static int __init rg280v_pm_mark_report(void)
{
\tvoid __iomem *rtc = ioremap(0x10003000, 0x40);

\tif (rtc) {
\t\tpr_info("RG280V PM marker: 0x%08x\\n", readl(rtc + 0x34));
\t\tiounmap(rtc);
\t}
\treturn 0;
}
late_initcall(rg280v_pm_mark_report);

'''
assert source.count(anchor) == 1
source = source.replace(anchor, helper + anchor)
for old, new in [
    ('\terror = platform_suspend_prepare(state);', '\trg280v_pm_mark(1);\n\terror = platform_suspend_prepare(state);'),
    ('\terror = dpm_suspend_late(PMSG_SUSPEND);', '\trg280v_pm_mark(2);\n\terror = dpm_suspend_late(PMSG_SUSPEND);'),
    ('\terror = platform_suspend_prepare_late(state);', '\trg280v_pm_mark(3);\n\terror = platform_suspend_prepare_late(state);'),
    ('\terror = dpm_suspend_noirq(PMSG_SUSPEND);', '\trg280v_pm_mark(4);\n\terror = dpm_suspend_noirq(PMSG_SUSPEND);'),
    ('\terror = platform_suspend_prepare_noirq(state);', '\trg280v_pm_mark(5);\n\terror = platform_suspend_prepare_noirq(state);'),
    ('\tif (suspend_test(TEST_PLATFORM))', '\trg280v_pm_mark(6);\n\tif (suspend_test(TEST_PLATFORM))'),
    (' Platform_wake:\n', ' Platform_wake:\n\trg280v_pm_mark(7);\n'),
    ('\tdpm_resume_noirq(PMSG_RESUME);', '\tdpm_resume_noirq(PMSG_RESUME);\n\trg280v_pm_mark(8);'),
    ('\tdpm_resume_early(PMSG_RESUME);', '\tdpm_resume_early(PMSG_RESUME);\n\trg280v_pm_mark(9);'),
    ('\tplatform_resume_finish(state);', '\tplatform_resume_finish(state);\n\trg280v_pm_mark(10);'),
]:
    assert source.count(old) == 1, old
    source = source.replace(old, new)

path.write_text(source)
