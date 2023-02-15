import os, re
from plasTeX import Command, log, TeXFragment, Element

from plasTeX.Packages.graphics import DeclareGraphicsExtensions as DeclareGraphicsExtensions_
from plasTeX.Packages.graphics import graphicspath as graphicspath_

class includegraphics(Command):
    args = '* [ options:dict ] file:str'
    packageName = 'graphicx'
    captionable = True

    def invoke(self, tex):
        res = Command.invoke(self, tex)

        f = self.attributes['file']
        ext = self.ownerDocument.userdata.getPath(
                      'packages/%s/extensions' % self.packageName,
                      ['.png','.jpg','.jpeg','.gif','.pdf','.ps','.eps'])
        paths = self.ownerDocument.userdata.getPath(
                        'packages/%s/paths' % self.packageName, ['.'])
        img = None

        # Check for file using graphicspath
        for p in paths:
            for e in ['']+ext:
                fname = os.path.join(p,f+e)
                if os.path.isfile(fname):
                    img = os.path.abspath(fname)
                    break
            if img is not None:
                break

        # Check for file using kpsewhich
        if img is None:
            for e in ['']+ext:
                try:
                    img = os.path.abspath(tex.kpsewhich(f+e))
                    break
                except (OSError, IOError):
                    pass

        options = self.attributes['options']

        if options is not None:

            scale = options.get('scale')
            if scale:
                scale = float(scale)
                if img.endswith('.pdf'):
                   w, h = 300, 300 ## FIXME: get pdf size
                elif img.endswith('.svg'):
                    import xml.etree.ElementTree as ET
                    attrs = ET.parse(img).getroot().attrib
                    w = int(attrs.get('width', 300))
                    h = int(attrs.get('height', 300))
                else:
                    from PIL import Image
                    w, h = Image.open(img).size
                self.style['width'] = '%spx' % (w * scale)
                self.style['height'] = '%spx' % (h * scale)

            def _convert(v, u="%"):
                import re
                if isinstance(v, Element):
                    if re.match(r"^(line|column|text)(width|height)$", v.nodeName): return "100"+u
                if isinstance(v, TeXFragment):
                    m = re.match(r"^\s*(\d*\.?\d+|\d+\.?)?\s*\\(line|column|text)(width|height)\s*$", v.source)
                    if m and m.group(1): return "%d%s" % (float(m.group(1))*100, u)
                    if m: return "100"+u
                return v

            height = options.get('height')
            width = options.get('width')
            if height is not None: self.style['height'] = _convert(height, "vh")
            if width is not None: self.style['width'] = _convert(width, "%")
            #log.warning("Height: {} width: {} -> h: {} w: {}".format(height.source if isinstance(height, TeXFragment) else height, width.source if isinstance(width, TeXFragment) else width, self.style.get("height"), self.style.get("width")))

            def getdimension(s):
                m = re.match(r'^([\d\.]+)\s*([a-z]*)$', s)
                if m and '.' in m.group(1):
                    return float(m.group(1)), m.group(2)
                elif m:
                    return int(m.group(1)), m.group(2)

            keepaspectratio = options.get('keepaspectratio')
            if img is not None and keepaspectratio == 'true' and \
               height is not None and width is not None:
                from PIL import Image
                w, h = Image.open(img).size

                height, hunit = getdimension(height)
                width, wunit = getdimension(width)

                scalex = float(width) / w
                scaley = float(height) / h

                if scaley > scalex:
                    height = h * scalex
                else:
                    width = w * scaley

                self.style['width'] = '%s%s' % (width, wunit)
                self.style['height'] = '%s%s' % (height, hunit)

        self.imageoverride = img

        return res

class DeclareGraphicsExtensions(DeclareGraphicsExtensions_):
    packageName = 'graphicx'

class graphicspath(graphicspath_):
    packageName = 'graphicx'

class rotatebox(Command):
    args = '[ options:dict ] angle:float self'
    packageName = 'graphicx'

