from plasTeX.Logging import getLogger
from plasTeX.Packages.amsmath import _AMSEquation, _AMSEquationStar

getLogger().warning('Package mathtools is not well supported by plasTeX or mathjax - please contribute.')

# Hack for removing "intertext" somewhat okayish. Alignment is still lost though, would need mathjax support!
# also, the text in intertext may be double escaped.
from plasTeX import Command, sourceChildren, sourceArguments
from plasTeX.Base.LaTeX.Math import MathEnvironment
class intertext(Command):
    args = 'self'
    mathMode = False

    @property
    def source(self):
        node = self.parentNode
        while node and not isinstance(node, MathEnvironment): node = node.parentNode
        if node: return u"\\end{{{0}}}\n{1}\n\\begin{{{0}}}{2}".format(node.tagName, str(self), sourceArguments(node))
        return Command.source(self) # fallback

class shortintertext(Command):
    args = 'self'
    mathMode = False

    @property
    def source(self):
        node = self.parentNode
        while node and not isinstance(node, MathEnvironment): node = node.parentNode
        if node: return u"\\end{{{0}}}\n{1}\n\\begin{{{0}}}{2}".format(node.tagName, str(self), sourceArguments(node))
        return Command.source(self) # fallback

class casesStar(_AMSEquationStar):
    macroName = "cases*"

class rcases(_AMSEquation):
    pass

class rcasesStar(_AMSEquationStar):
    macroName = "rcases*"

class dcases(_AMSEquation):
    pass

class dcasesStar(_AMSEquationStar):
    macroName = "dcases*"

class drcases(_AMSEquation):
    pass

class drcasesStar(_AMSEquationStar):
    macroName = "drcases*"

class smallmatrix(Array):
    pass

class smallmatrixStar(Array):
    macroName = "smallmatrix*"

class bsmallmatrix(Array):
    pass

class bsmallmatrixStar(Array):
    macroName = "bsmallmatrix*"

class Bsmallmatrix(Array):
    pass

class BsmallmatrixStar(Array):
    macroName = "Bsmallmatrix*"

class vsmallmatrix(Array):
    pass

class vsmallmatrixStar(Array):
    macroName = "vsmallmatrix*"

class Vsmallmatrix(Array):
    pass

class VsmallmatrixStar(Array):
    macroName = "Vsmallmatrix*"

class bmatrixStar(Array):
    macroName = "bmatrix*"

class BmatrixStar(Array):
    macroName = "Bmatrix*"

class vmatrixStar(Array):
    macroName = "vmatrix*"

class VmatrixStar(Array):
    macroName = "Vmatrix*"

