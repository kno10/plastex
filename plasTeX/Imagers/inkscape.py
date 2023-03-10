import subprocess
import re
from typing import List, Tuple
from plasTeX.Imagers import VectorImager, scale_svg, scour

class Inkscape(VectorImager):
    """ Imager that uses inkscape """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which inkscape']
    compiler = 'pdflatex'

    def executeConverter(self, outfile=None) -> List[Tuple[str, str]]:
        if outfile is None:
            outfile = self.tmpFile.with_suffix('.pdf').name

        images = []
        for no, line in enumerate(open("images.csv")):
            filename = 'img%d.svg' % no
            page, output, scale_str = line.split(",")
            scale = float(scale_str.strip())

            subprocess.run(['inkscape', '--pdf-poppler', '-D', '-l', '-o', filename, '--pdf-page', str(page), outfile], stdout=subprocess.DEVNULL, check=True)

            if scale != 1:
                scale_svg(filename, scale)
            scour(filename)

            images.append((filename, output.rstrip()))

        return images

Imager = Inkscape
