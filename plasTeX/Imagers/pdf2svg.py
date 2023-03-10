import subprocess
import re
from typing import List, Tuple
from plasTeX.Imagers import VectorImager, scale_svg, scour

class PDFSVG(VectorImager):
    """ Imager that uses pdf2svg """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which pdf2svg', 'pdfcrop --help']
    compiler = 'pdflatex'

    def executeConverter(self, outfile=None) -> List[Tuple[str, str]]:
        if outfile is None:
            outfile = self.tmpFile.with_suffix('.pdf').name

        subprocess.call(["pdfcrop", outfile, self.tmpFile.with_suffix('.cropped.pdf').name], stdout=subprocess.DEVNULL)

        images = []
        for no, line in enumerate(open("images.csv")):
            filename = 'img%d.svg' % no
            page, output, scale_str = line.split(",")
            scale = float(scale_str.strip())

            subprocess.run(['pdf2svg', self.tmpFile.with_suffix('.cropped.pdf').name, filename, str(page)], stdout=subprocess.DEVNULL, check=True)

            if scale != 1:
                scale_svg(filename, scale)
            scour(filename)

            images.append((filename, output.rstrip()))

        return images


Imager = PDFSVG
