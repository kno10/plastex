"""
Enquote package, minimal support.

TODO: determine nesting level in the parser directly?
"""
from plasTeX import Command

class enquote(Command):
    args = "self"

class foreignquote(Command):
    args = "language self"

class openautoquote(Command):
    pass

class closeautoquote(Command):
    pass
