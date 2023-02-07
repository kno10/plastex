import subprocess, shlex
import os, shutil, re
from pathlib import Path
from typing import IO
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer
from plasTeX.Renderers.Markdown.Config import addConfig
from plasTeX.Logging import getLogger

log = getLogger()

class Markdown(_Renderer):
    """Renderer targetting Markdown."""

    fileExtension = '.md'
    imageTypes = ['.svg', '.png','.jpg','.jpeg','.gif', '.pdf']
    vectorImageTypes = ['.svg', '.pdf']
    vectorBitmap = False

    def loadTemplates(self, document):
        """Load templates as in PageTemplate but also look for packages that
        want to override some templates and handles extra css and javascript."""

        _Renderer.loadTemplates(self, document)
        rendererdata = document.rendererdata.setdefault('markdown', dict())
        config = document.config
        if 'markdown' not in config:
            addConfig(config)

        srcDir = document.userdata.get('working-dir', '.') # type: str
        buildDir = os.getcwd()

    def processFileContent(self, document, s):
        s = _Renderer.processFileContent(self, document, s)

        # Trim triple newlines to double
        s = re.sub(r'\n\n\n+', r'\n\n', s)
        # Remove empty paragraphs
        #s = re.compile(r'<p>\s*</p>', re.I).sub(r'', s)

        # Add a non-breaking space to empty table cells
        #s = re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I).sub(r'\1&nbsp;\3', s)

        for fun in document.rendererdata['markdown'].get('processFileContents', []):
            s = fun(document, s)

        #filters = document.config['markdown']['filters']
        #for filter_ in filters:
        #    proc = subprocess.Popen(
        #            shlex.split(filter_),
        #            stdin=subprocess.PIPE,
        #            stdout=subprocess.PIPE)
        #    output, output_err = proc.communicate(s.encode(encoding="utf-8"))
        #    if not output_err:
        #        s = output.decode(encoding="utf-8")

        return s

    def cleanup(self, document, files, postProcess=None):
        """
        Cleanup method called at the end of rendering.
        Uses the base renderer cleanup but calls packages callbacks before and
        after. Callbacks should be listed in
        document.userdata['preCleanupCallbacks']
        or document.userdata['postCleanupCallbacks']. Each call back should accept the
        current document as its only argument. Pre-cleanup call back must return
        the list of path of files they created (relative to the output directory).
        """

        rendererdata = document.rendererdata.get('markdown', dict())
        preCleanupCallbacks = rendererdata.get('preCleanupCallbacks', [])
        for preCleanupCallback in preCleanupCallbacks:
            files += preCleanupCallback(document)

        _Renderer.cleanup(self, document, files, postProcess)


Renderer = Markdown
