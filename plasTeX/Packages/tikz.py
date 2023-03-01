"""
Implement the tikz package using the imager
"""
from plasTeX import VerbatimEnvironment, Command, Environment

class tikzpicture(VerbatimEnvironment):
    #causes parsing problems when there are no options? #args = "[ options:dict ]"
    pass

class tikz(Command):
    args = "[ options:dict ] self"
    pass

class usetikzlibrary(Command):
    args = "library"

class tikzset(Command):
    args = "library"

class tikzstyle(Command):
    args = "{ key:str } = [ val:str ]"
