"""
Enquote package, minimal support
"""
from plasTeX import Command

class enquote(Command):
    args = "self"

class foreignquote(Command):
    args = "language self"
