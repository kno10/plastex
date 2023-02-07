from plasTeX.ConfigManager import *
from plasTeX.DOM import Node

class MacrosOption(DictOption[str]):
    @classmethod
    def entryFromString(cls, entry: str) -> str:
        return entry

    def registerArgparse(self, group: ArgumentGroup):
        group.add_argument(*self.options, dest=self.name,
                           help=self.description, action='append',
                           nargs=2, metavar=("MACRO", "VALUE"))

def addConfig(config: ConfigManager):
    section = config.addSection('markdown', 'Markdown renderer Options')

#    section['use-mathjax'] = BooleanOption(
#        """ Use mathjax """,
#        options='--use-mathjax !--no-mathjax',
#        default=True,
#    )
#
#    section['mathjax-url'] = StringOption(
#        """ Url of the MathJax lib """,
#        options='--mathjax-url',
#        default='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js',
#    )
#
#    section['mathjax-dollars'] = BooleanOption(
#        """ Use single dollars as math delimiter for mathjax """,
#        options='--dollars !--no-dollars',
#        default=False,
#    )
#
#    section['filters'] = MultiStringOption(
#        """Comma separated list of commands to invoke on each output page.""",
#        options='--filters',
#        default=[],
#    )
