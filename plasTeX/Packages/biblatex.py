r"""
biblatex

TODO:
- everything
- cross-version compatibility?
- punctuation styles?
- add compression for numeric (c.f., natbib)?
- compressed display of same authors?
- make maxnames configurable
"""

import re, string
from plasTeX import Base, Text, log

log.warning('Package biblatex is currently only a limited stub, and may be tailored to a specific biblatex version, unfortunately!')

# TODO: get style from package!

class bstyleoption(Text):
    """ Option that can only be overridden by package options,
        citestyle, or bibpunct """

def ProcessOptions(options, document):
    """ Process package options """
    default_options = {
                'maxcitenames': 3,
                'maxbibnames': 999,
            }
    options = options or dict()
    new_options = dict()
    punct = {'post': bstyleoption(', '),
             'open': bstyleoption('['),
             'close':bstyleoption(']'),
             'sep':  bstyleoption(';'),
             'style':bstyleoption('a'),
             'dates':bstyleoption(','),
             'years':bstyleoption(',')}
    # TODO: support various options!
    document.userdata['biblatex'] = {**default_options, **options, **new_options, 'punctuation': punct}

def _format_names(authors, maxnames=999):
    if not authors:
        return None
    au = []
    trunc = len(authors) if not maxnames or len(authors) <= maxnames else maxnames - 1
    for i, a in enumerate(authors[:trunc]):
        if i > 0:
            au.append(", " if i < len(authors) - 1 else ", and ")
        g, f = a.get("given"), a.get("family")
        if g: g = "".join(str(x) for x in g)
        if f: f = "".join(str(x) for x in f)
        if not f:
            au.append("?")
        elif g:
            au.extend((g, " ", f))
        else:
            au.append(f)
    if trunc < len(authors):
        au.append("et al.") # TODO: use parsed "et al.{}" in case we output to tex?
    return au if au else ["?"]

class biblatexitem(Base.Command):
    def __init__(self):
        self.bibitem = dict()

    @property
    def authorstr(self):
        return "".join(_format_names(self.bibitem.get("author"), self.ownerDocument.userdata['biblatex'].get("maxbibnames")))

    @property
    def editorstr(self):
        return "".join(_format_names(self.bibitem.get("editor"), self.ownerDocument.userdata['biblatex'].get("maxbibnames")))

    @property
    def title(self):
        return str(self.bibitem.get("title"))

class addbibresource(Base.Command):
    args = 'filename:str'
    # needs to be processed by bibtex/biber

class biblatexsty(Base.Command):
    macroName = 'ver@biblatex.sty' # biblatex .bbl tests for this name to be defined

class printbibliography(Base.bibliography):
    args = '[ options:dict ]'
    level = Base.Node.ENVIRONMENT_LEVEL
    blockType = True

    class setcounter(Base.Command):
        # Added so that setcounters in the aux file don't mess counters up
        args = 'name:nox num:nox'

    def loadBibliographyFile(self, tex):
        doc = self.ownerDocument
        # Clear out any bib info from the standard package.
        # We have to get our info from the aux file.
        self.ownerDocument.userdata.setPath('bibliography/bibcites', {})
        self.ownerDocument.context.push(self)
        self.ownerDocument.context['setcounter'] = self.setcounter
        tex.loadAuxiliaryFile()
        self.ownerDocument.context.pop(self)
        Base.bibliography.loadBibliographyFile(self, tex)

    @property
    def bibitems(self):
        return self.ownerDocument.userdata.getPath('bibliography/bibcites', {})

class refsection(Base.Environment):
    args = 'sect:int'
    level = Base.Node.OUTER_ENVIRONMENT_LEVEL
    blockType = True

    class datalist(Base.Environment):
        args = '[ type:str ] name:str'  
        level = Base.Node.OUTER_ENVIRONMENT_LEVEL
        blockType = True

        class endentry(Base.Command):
            def invoke(self, tex):
                end = self.ownerDocument.createElement(self.nodeName[3:])
                end.parentNode = self.parentNode
                end.macroMode = Base.Environment.MODE_END

                doc = self.ownerDocument
                bibcites = self.ownerDocument.userdata.getPath('bibliography/bibcites', {})
                curbib = self.ownerDocument.userdata.getPath('bibliography/curbib')
                bibcites[curbib.bibitem["key"]] = curbib
                #for k,v in curbib.bibitem.items(): print(k, v.textContent if hasattr(v, "textContent") else str(v))
                self.ownerDocument.userdata.setPath('bibliography/bibcites', bibcites)
                self.ownerDocument.userdata.setPath('bibliography/curbib', None)
                self.ownerDocument.userdata.setPath('bibliography/curverb', None)
                return [end]

    class entry(Base.Command):
        args = 'key:str type:str option:str'

        def __init__(self):
            self.bibitem = dict()

        def invoke(self, tex):
            super().invoke(tex)
            self.id = self.attributes["key"]
            #self.ownerDocument.context.push(self) # to find "biblatexitem"
            curbib = self # self.ownerDocument.createElement('biblatexitem')
            self.ownerDocument.userdata.setPath('bibliography/curbib', curbib)
            curbib.bibitem["key"] = self.attributes["key"]
            #self.ownerDocument.context.pop(self)

        @property
        def authorstr(self):
            return "".join(_format_names(self.bibitem.get("author"), self.ownerDocument.userdata['biblatex'].get("maxbibnames")))

        @property
        def editorstr(self):
            return "".join(_format_names(self.bibitem.get("editor"), self.ownerDocument.userdata['biblatex'].get("maxbibnames")))

        @property
        def title(self):
            return str(self.bibitem.get("title"))

        @property
        def year(self):
            return str(self.bibitem.get("year"))

    class List(Base.Command):
        macroName = "list"
        args = 'field:str count:int entries'

        def invoke(self, tex):
            super().invoke(tex)
            #print(self.attributes["entries"].textContent)
            curbib = self.ownerDocument.userdata.getPath('bibliography/curbib')
            curbib.bibitem[self.attributes["field"]] = [tex.normalize(x) for x in self.attributes["entries"]]

    class Name(Base.Command):
        macroName = "name"
        args = 'field:str count:int option:str'

        def invoke(self, tex):
            Base.Command.invoke(self, tex)
            self.ownerDocument.context.push(self)
            # Now parse the entries field:
            tok = next(tex.itertokens())
            assert tok.catcode == Base.Token.CC_BGROUP, "biblatex name missing entries field?"
            entries = []
            for i in range(int(self.attributes["count"])):
                tok = next(tex.itertokens())
                assert tok.catcode == Base.Token.CC_BGROUP, "biblatex entry should be nested groups"
                # read the hash key, ignored
                output, source = tex.readToken(False, parentNode=self)
                # now read the key-value author information
                output, source = tex.readToken(True, parentNode=self)
                tok = next(tex.itertokens())
                assert tok.catcode == Base.Token.CC_EGROUP, "biblatex entry should be nested groups"
                ent = tex.castDictionary(output)
                #for k, v in ent.items():
                for k, v in ent.items():
                    #ent[k] = tex.normalize(v)
                    if isinstance(v, Base.bgroup): ent[k] = "".join(x.textContent for x in v.childNodes)
                #print("Dict", ", ".join(map(lambda i: "%s: %s" % (i[0], i[1]), ent.items())))
                entries.append(ent)
            tok = next(tex.itertokens())
            assert tok.catcode == Base.Token.CC_EGROUP, "biblatex name entries field inconsistent?"
            curbib = self.ownerDocument.userdata.getPath('bibliography/curbib')
            curbib.bibitem[self.attributes["field"]] = entries
            self.ownerDocument.context.pop(self)

        class bibinitdelim(Base.Command):
            str = u" " # non-breaking

        class bibinithyphendelim(Base.Command):
            str = "-"

        class bibinitperiod(Base.Command):
            str = "."

        class bibnamedelima(Base.Command):
            str = " " # regular space

        class bibnamedelimb(Base.Command):
            str = " " # regular space

        class bibnamedelimc(Base.Command):
            str = " " # regular space

        class bibnamedelimd(Base.Command):
            str = " " # regular space

        class bibnamedelimi(Base.Command):
            str = u" " # non-breaking

    class keyw(Base.Command):
        args = 'value'

        def invoke(self, tex):
            Base.Command.invoke(self, tex)
            curbib = self.ownerDocument.userdata.getPath('bibliography/curbib')
            curbib.bibitem["keywords"] = tex.normalize(self.attributes.get("value"))

    class strng(Base.Command):
        args = 'field:str value'

        def invoke(self, tex):
            Base.Command.invoke(self, tex)
            if self.attributes["field"].endswith("hash"): return
            curbib = self.ownerDocument.userdata.getPath('bibliography/curbib')
            curbib.bibitem[self.attributes["field"]] = tex.normalize(self.attributes.get("value"))

    class field(Base.Command):
        args = 'field:str value'

        def invoke(self, tex):
            Base.Command.invoke(self, tex)
            if self.attributes["field"].endswith("hash"): return
            curbib = self.ownerDocument.userdata.getPath('bibliography/curbib')
            curbib.bibitem[self.attributes["field"]] = tex.normalize(self.attributes.get("value"))

    class range(Base.Command):
        args = 'field:str value'

        def invoke(self, tex):
            Base.Command.invoke(self, tex)
            curbib = self.ownerDocument.userdata.getPath('bibliography/curbib')
            curbib.bibitem[self.attributes["field"]] = tex.normalize(self.attributes.get("value"))

    class endverb(Base.Command):
        def invoke(self, tex):
            return []

    class verb(Base.Command):
        r"""\verb is tricky, because it exists as \verb{str} and \verb text \endverb"""

        def invoke(self, tex):
            #if self.macroMode == Base.Macro.MODE_END: return
            self.ownerDocument.context.push(self)
            #self.parse(tex)
            tok = next(tex.itertokens())
            tex.pushToken(tok) # push back to parse entirely
            output, source = tex.readToken(False, parentNode=self)
            if tok.catcode == Base.Token.CC_BGROUP:
                self.attributes["value"] = tex.normalize(output)
                self.argSources = { "value": source }
                self.argSource = source
            else:
                #self.macroMode = Base.Macro.MODE_BEGIN
                self.ownerDocument.context.setVerbatimCatcodes()
                while not source.endswith(r"\endverb"):
                    o, s = tex.readToken(False, parentNode=self)
                    output += o
                    source += s
                assert len(output) == len(source)
                output = output[:-8]
                source = source[:-8]
                self.attributes["value"] = tex.normalize(output)
                self.argSources = { "value": source }
                self.argSource = source
            # verb appear to always come in pairs, usually \verb{key}\verb content\endverb
            # FIXME: is this guaranteed?
            curverb = self.ownerDocument.userdata.getPath('bibliography/curverb')
            if curverb:
                curbib = self.ownerDocument.userdata.getPath('bibliography/curbib')
                curbib.bibitem[curverb] = self.attributes["value"]
                self.ownerDocument.userdata.setPath('bibliography/curverb', None)
            else:
                self.ownerDocument.userdata.setPath('bibliography/curverb', self.attributes["value"])
            self.ownerDocument.context.pop(self)

        def Xdigest(self, tokens):
            #if self.macroMode == Base.Macro.MODE_END: return
            tok = next(iter(tokens))
            print("digest", self, tok)
            self.appendChild(tok)
            if isinstance(tok, Base.bgroup):
                for item in tokens:
                    if tok.contextDepth < self.contextDepth:
                        tokens.push(tok)
                        break
                    print("digest2", self, item)
                    self.appendChild(item)
                    if isinstance(item, Base.egroup):
                        break
            else:
                #self.macroMode = Base.Macro.MODE_BEGIN
                for item in tokens:
                    if tok.contextDepth < self.contextDepth:
                        tokens.push(tok)
                        break
                    self.appendChild(item)
                    print("digest3", self, item)
                    if item.nodeType == Base.Command.ELEMENT_NODE and item.nodeName == 'endverb':
                        #item.macroMode = Base.Macro.MODE_END
                        break

    class bibrangedash(Base.Command):
        str = "-"

    class enddatalist(Base.Command):
        def invoke(self, tex):
            end = self.ownerDocument.createElement(self.nodeName[3:])
            end.parentNode = self.parentNode
            end.macroMode = Base.Environment.MODE_END
            return [end]

class endrefsection(Base.Command):
    def invoke(self, tex):
        end = self.ownerDocument.createElement(self.nodeName[3:])
        end.parentNode = self.parentNode
        end.macroMode = Base.Environment.MODE_END
        return [end]

class BiblatexCite(Base.cite):
    """ Base class for all natbib-style cite commands """
    args = '* [ text ] [ text2 ] bibkeys:list:str'

    @property
    def punctuation(self):
        return self.ownerDocument.userdata['biblatex']['punctuation']

    @property
    def bibopt(self):
        return self.ownerDocument.userdata['biblatex']

    @property
    def bibitems(self):
        items = []
        b = self.ownerDocument.userdata.getPath('bibliography/bibcites', {})
        for key in self.attributes['bibkeys']:
            if key in b:
                items.append(b[key])
            else:
                log.warning("Unresolved bib key: {}".format(key))
                items.append(key)
        return items

    @property
    def prenote(self):
        """ Text that comes before the citation """
        a = self.attributes
        if a.get('text2') is not None and a.get('text') is not None:
            if not a.get('text').textContent.strip():
                return ''
            out = self.ownerDocument.createElement('bgroup')
            out.extend(a['text'])
            out.append(' ')
            return out
        return ''

    @property
    def postnote(self):
        """ Text that comes after the citation """
        a = self.attributes
        if a.get('text2') is not None and a.get('text') is not None:
            if not a.get('text2').textContent.strip():
                return ''
            out = self.ownerDocument.createElement('bgroup')
            out.append(self.punctuation['post'])
            out.extend(a['text2'])
            return out
        elif a.get('text') is not None:
            if not a.get('text').textContent.strip():
                return ''
            out = self.ownerDocument.createElement('bgroup')
            out.append(self.punctuation['post'])
            out.extend(a['text'])
            return out
        return ''

    @property
    def separator(self):
        """ Separator for multiple items """
        return self.punctuation['sep']

    @property
    def dates(self):
        """ Separator between author and dates """
        return self.punctuation['dates']

    @property
    def years(self):
        """ Separator for multiple years """
        return self.punctuation['years']

    def isNumeric(self):
        return self.punctuation['style'] in ['n','s']

    def citeValue(self, item):
        """ Return cite value based on current style """
        b = self.ownerDocument.createElement('bibliographyref')
        if hasattr(item, "bibitem"):
            b.idref['bibitem'] = item
            b.append(item.bibitem.get("labelalpha", "?")) # TODO: was: item.bibcite or year
        else:
            b.append(item) # key
        return b

    def capitalize(self, item):
        """ Capitalize the first text node """
        if isinstance(item, str): return item.capitalize()
        if isinstance(item, list): return [self.capitalize(x) for x in item]
        item = item.cloneNode(True)
        textnodes = [x for x in item.allChildNodes
                       if x.nodeType == self.TEXT_NODE]
        if not textnodes:
            return item
        node = textnodes.pop(0)
        node.parentNode.replaceChild(node.cloneNode(True).capitalize(), node)
        return item

    def numcitation(self):
        """ Numeric style citations """
        res = []
        for i, item in enumerate(self.bibitems):
            if i > 0:
               res.append(self.punctuation['sep'])
            frag = self.ownerDocument.createDocumentFragment()
            frag.append(item.ref)
            frag.idref = item
            res.append(frag)
        return res


class parencite(BiblatexCite):
    """Cite with parens"""
    def numcitation(self):
        """ Numeric style citations """
        return [self.punctuation['open']] + super().numcitation() + [self.punctuation['close']]

    def citation(self):
        if self.isNumeric():
            return self.numcitation()

        res = [self.punctuation['open'], self.prenote]
        for i, item in enumerate(self.bibitems):
            if i > 0:
                res.append(self.punctuation['sep']+' ')
            if not hasattr(item, "bibitem"):
                res.append(item)
                continue
            res.extend(_format_names(item.bibitem.get("author", self.bibopt.get("maxcitenames"))))
            res.append(self.punctuation['sep'])
            res.append(str(item.bibitem.get("year", "?")))
        res.extend([self.postnote, self.punctuation['close']])
        return res

class citep(parencite):
    """Only with natbib=true, actually"""
    pass

class textcite(BiblatexCite):
    def citation(self, full=False, capitalize=False):
        """ Jones et al. (1990) """
        if self.isNumeric():
            return self.numcitation()
        res = self.ownerDocument.createDocumentFragment()
        bibitems = self.bibitems
        for i, item in enumerate(bibitems):
            if i > 0:
                res.append(self.separator+' ')
            if not hasattr(item, "bibitem"):
                res.append(item)
                continue
            res.extend(self.capitalize(_format_names(item.bibitem.get("author"), self.bibopt.get("maxcitenames"))))
            res.append(' ')
            res.append(self.punctuation['open'])
            # Prenote
            if i == 0:
                res.append(self.prenote)
            # Year or text
            res.append(self.citeValue(item))
            # Postnote, and closing punctuation
            if i == len(bibitems) - 1:
                res.append(self.postnote)
            res.append(self.punctuation['close'])
        return res

    def numcitation(self):
        """ Numeric style citations, always with brackets """
        return [self.punctuation['open']] + super().numcitation() + [self.punctuation['close']]

class citet(textcite):
    """Only with natbib=true, actually"""
    pass

class citetext(textcite):
    """Only with natbib=true, actually"""
    pass

class citeauthor(BiblatexCite):
    def citation(self, full=False, capitalize=False):
        """ Jones et al. """
        if self.isNumeric():
            return self.numcitation()
        res = self.ownerDocument.createDocumentFragment()
        bibitems = self.bibitems
        res.append(self.prenote)
        for i, item in enumerate(bibitems):
            if i > 0:
                res.append(self.separator+' ')
            if hasattr(item, "bibitem"):
                res.extend(self.capitalize(_format_names(item.bibitem.get("author"), self.bibopt.get("maxcitenames"))))
            else:
                res.append(item)
        res.append(self.postnote)
        return res

    def numcitation(self):
        """ Numeric style citations, always with brackets """
        return [self.punctuation['open']] + super().numcitation() + [self.punctuation['close']]

class cite(BiblatexCite):
    """Symbolic cite, make configurable?"""
    def citation(self, full=False, capitalize=False):
        bibitems = self.bibitems
        res = self.ownerDocument.createDocumentFragment()
        for i, item in enumerate(bibitems):
            if i > 0:
                res.append(self.separator+' ')
            res.append(self.citeValue(item))
        return res

class fullcite(textcite):
    """Fixme, should be full bibitem"""
    pass
