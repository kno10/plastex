"""
Implement the algorithm2e package as verbatim
"""
from plasTeX import VerbatimEnvironment
from plasTeX import Command

class algorithm(VerbatimEnvironment):
    args = "[ options:dict ]"
    pass

class IncMargin(Command):
    args = "depth:dimen"

class DecMargin(Command):
    args = "depth:dimen"
