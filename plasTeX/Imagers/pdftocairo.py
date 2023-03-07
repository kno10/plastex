import subprocess
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple
from plasTeX.Imagers import VectorImager

length_re = re.compile('([0-9\\.]*)(.*)')
class PDFSVGCairo(VectorImager):
    """ Imager that uses pdftocairo """
    fileExtension = '.svg'
    # TODO: make scour optional
    verifications = ['pdflatex --help', 'which pdftocairo', 'pdfcrop --help', 'scour --help']
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
            images.append((filename, output.rstrip()))

            subprocess.run(['pdftocairo', '-svg', '-nocrop', self.tmpFile.with_suffix('.cropped.pdf').name, filename, '-f', str(page), '-l', str(page)], stdout=subprocess.DEVNULL, check=True)

            if scale != 1:
                tree = ET.parse(filename)
                root = tree.getroot()

                for attrib in ["width", "height"]:
                    m = length_re.match(root.attrib[attrib])
                    if m is None:
                        raise ValueError
                    root.attrib[attrib] = "{:.3f}{}".format(float(m.group(1)) * scale, m.group(2))

                tree.write(filename)

            cmd = ['scour', '-q', '--indent=none', '-o', filename]
            subprocess.run(cmd, input=open(filename,"rb").read(), check=True)

        return images

Imager = PDFSVGCairo
