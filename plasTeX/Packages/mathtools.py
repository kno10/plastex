from plasTeX.Logging import getLogger

getLogger().warning('Package mathtools is not well supported by plasTeX or mathjax.')

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

