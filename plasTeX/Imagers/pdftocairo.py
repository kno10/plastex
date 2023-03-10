import subprocess
import re
from typing import List, Tuple
from plasTeX.Imagers import VectorImager, scale_svg, scour

class PDFSVGCairo(VectorImager):
    """ Imager that uses pdftocairo """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which pdftocairo', 'pdfcrop --help']
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

            subprocess.run(['pdftocairo', '-svg', '-nocrop', self.tmpFile.with_suffix('.cropped.pdf').name, filename, '-f', str(page), '-l', str(page)], stdout=subprocess.DEVNULL, check=True)

            if scale != 1:
                scale_svg(filename, scale)
            scour(filename)

            images.append((filename, output.rstrip()))

        return images

Imager = PDFSVGCairo
