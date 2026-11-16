#!/usr/bin/env python3
"""Diagnostic only: keep the JZ4770 OST clock running during PM tests."""

from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text()
old = '''static int ingenic_ost_suspend(struct device *dev)
{
\tstruct ingenic_ost *ost = dev_get_drvdata(dev);

\tclk_disable(ost->clk);

\treturn 0;
}

static int ingenic_ost_resume(struct device *dev)
{
\tstruct ingenic_ost *ost = dev_get_drvdata(dev);

\treturn clk_enable(ost->clk);
}'''
new = '''static int ingenic_ost_suspend(struct device *dev)
{
\t/* RG280V diagnostic: leave the active clocksource running. */
\treturn 0;
}

static int ingenic_ost_resume(struct device *dev)
{
\treturn 0;
}'''
assert source.count(old) == 1
path.write_text(source.replace(old, new))
