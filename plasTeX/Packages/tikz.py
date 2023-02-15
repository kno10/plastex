"""
TODO: Implement the tikz package using the imager
"""
from plasTeX import VerbatimEnvironment, Command, Environment

class tikzpicture(VerbatimEnvironment):
    pass

class tikz(Command):
    args = "[ options:str ] self"
    pass

class usetikzlibrary(Command):
    args = "library"

class tikzset(Command):
    args = "library"

class tikzstyle(Command):
    args = "{ key:str } = [ val:str ]"
