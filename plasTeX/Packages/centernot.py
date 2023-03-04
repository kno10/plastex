"""
Centernot command, supported by mathjax extension

MathJax also has centerOver, but that does not seem to be in LaTeX?
"""
from plasTeX import Command

class centernot(Command):
    args = "self"
