"""
Stub for relsize, not really supported in any output yet.
"""
from plasTeX import Command

class relsize(Command):
    args = "{ size:int }"

class larger(Command):
    args = "[ size:int ]"

class smaller(Command):
    args = "[ size:int ]"

class textlarger(Command):
    args = "[ size:int ] self"

class textsmaller(Command):
    args = "[ size:int ] self"

class relscale(Command):
    args = "{ size:float }"

class textscale(Command):
    args = "{ size:float } self"
