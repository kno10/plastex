"""
Centernot command, supported by mathjax extension
"""
from plasTeX import Command

class centernot(Command):
    args = "symv"

class centerOver(Command):
    """Currently only in MathJax! Copy and modify the centernot.sty if you use this."""
    args = "symb1 symb2"
