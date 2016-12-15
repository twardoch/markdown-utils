#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""docxtomd
  Word .docx to Markdown converter
  Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
  https://github.com/twardoch/markdown-utils

This tool converts a Word .docx file to Markdown using pandoc. 
Unlike pandoc, it intelligently converts and names the vector 
or bitmap images contained in the .docx into either .svg or .png. 

example: 
  $ ./docxtomd.py --html -d test/test1 test/test1.docx
"""

__version__ = "0.4.2"

import os
import warnings
import sys
import os.path
import sh
import argparse
import subprocess
import shutil
import fnmatch
import string
import json
import wmftosvgpng
import codecs
try: 
    import markdown
    MARKDOWN = True
except ImportError: 
    MARKDOWN = False

def ExtractAlphanumeric(InputString):
    return "".join([ch for ch in InputString if ch in (string.ascii_letters + string.digits)])

class DocxToMdConverter(object): 

    def __init__(self, **opts):
        self.inputpath = opts.get("inputpath", None)
        self.outputpath = opts.get("outputpath", None)
        self.outfolder = opts.get("out_dir", None)
        self.format = opts.get("format", "docx")
        self.toc = opts.get("toc", False)
        self.pandoc = opts.get("pandoc", "/usr/local/bin/pandoc")
        self.wmf2svg = opts.get("wmf2svg", "/usr/local/java/wmf2svg.jar")
        self.verbose = opts.get("verbose", False)
        self.debug = opts.get("debug", False)
        self.jsonpath = opts.get("jsonpath", None)
        self.imgfolder = opts.get("img_dir", None)
        self.html = opts.get("html", False)
        self.keepdim = opts.get("keep_dimensions", False)
        self.success = True
        self.stdout = None
        self.stderr = None
        self.mediafolder = self.imgfolder
        self.cwd = os.path.dirname(os.path.realpath(os.getcwd()))

    def preparePaths(self): 
        if not self.inputpath: 
            self.success = False
        self.inputpath = os.path.realpath(os.path.normpath(self.inputpath))
        if not os.path.exists(self.inputpath): 
            self.success = False
        if not self.outputpath: 
            self.outputpath = os.path.splitext(self.inputpath)[0] + ".md"
        self.outputpath = os.path.realpath(os.path.normpath(self.outputpath))
        if self.outfolder: 
            self.outfolder = os.path.realpath(os.path.normpath(self.outfolder))
            self.outputpath = os.path.join(self.outfolder, os.path.basename(self.outputpath))
        else: 
            self.outfolder = os.path.dirname(self.outputpath)
        if not os.path.exists(self.outfolder): 
            try: 
                os.makedirs(self.outfolder)
            except: 
                warnings.warn("Cannot create folder %s" % (self.outfolder))
                self.success = False
        if not self.imgfolder: 
            self.imgfolder = os.path.join(self.outfolder, "img")
        if not os.path.exists(self.imgfolder): 
            try: 
                os.makedirs(self.imgfolder)
            except: 
                warnings.warn("Cannot create folder %s" % (self.imgfolder))
                self.success = False
        self.mediaprefix = ExtractAlphanumeric(os.path.splitext(os.path.basename(self.outputpath))[0])
        if not self.jsonpath: 
            self.jsonpath = os.path.join(self.outfolder, self.mediaprefix + ".doc.json")

    def pandocRun(self, args): 
        # To get access to pandoc-citeproc when we use a included copy of pandoc,
        # we need to add the pypandoc/files dir to the PATH
        new_env = os.environ.copy()
        files_path = os.path.join(self.cwd, "files")
        new_env["PATH"] = new_env.get("PATH", "") + os.pathsep + files_path

        if self.debug: 
            print("Running: " + " ".join(args))
        p = subprocess.Popen(args, bufsize=4096, stdin=None, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=new_env, cwd=self.cwd)
        if not (p.returncode is None):
            raise RuntimeError(
                'Pandoc died with exitcode "%s" before receiving input: %s' % (p.returncode,
                                                                               p.stderr.read())
            )
        try:
            self.stdout, self.stderr = p.communicate(None)
            self.success = True
        except OSError:
            raise RuntimeError('Pandoc died with exitcode "%s" during conversion.' % (p.returncode))
            self.success = False
        assert self.stdout == ""

    def prepareMedia(self): 
        self.mediamap = {}

        for pngfn in fnmatch.filter(os.listdir(self.mediafolder), '*.png'): 
            self.mediamap[pngfn] = pngfn
        for wmffn in fnmatch.filter(os.listdir(self.mediafolder), '*.wmf'): 
            fullsrc = os.path.join(self.mediafolder, wmffn)
            fulloutbase = os.path.splitext(fullsrc)[0]
            rettype, retpath = wmftosvgpng.toSvgOrPng(**{
                'inputpath': fullsrc, 'outputbase': fulloutbase, 
                'compress': False, 'verbose': False, 'remove': not self.debug, 
                'wmf2svg': self.wmf2svg,
            })
            if rettype: 
                retfn = os.path.basename(retpath)
                self.mediamap[wmffn] = retfn
        self.mediainfopath = os.path.join(self.outfolder, self.mediaprefix + ".media.json")
        mediainfofile = file(self.mediainfopath, "w")
        json.dump({
            "keepdim": self.keepdim, 
            "srcfull": self.mediafolder, 
            "dstfull": self.imgfolder,
            "prefix": self.mediaprefix, 
            "srcsubstr": u"./media/", 
            "dstsubstr": u"img/", 
            "map": self.mediamap
        }, mediainfofile)
        mediainfofile.close()
        os.environ['pandoc_mapmedia_info'] = self.mediainfopath

    def convertJsonToMd(self): 
        pdArgs = ['--smart', '--section-divs', '--atx-headers']
        if self.toc: 
            pdArgs.append('--toc')

        pdFilters = [os.path.join(os.path.dirname(__file__),'pandoc_mapmedia.py')]

        pdMdExt = [
            '+pipe_tables', '+auto_identifiers', '+backtick_code_blocks', 
            '+blank_before_blockquote', '+blank_before_header', '+bracketed_spans', 
            '+definition_lists', '+escaped_line_breaks', '+fenced_code_attributes', 
            '+footnotes', '+header_attributes', '+implicit_header_references', 
            '+line_blocks', '+pandoc_title_block'
            ]
        pdMdOutFmt = 'markdown_github' + ''.join(pdMdExt)

        args = [self.pandoc]
        args.append('--from=' + 'json')
        args.append('--to=' + pdMdOutFmt)
        args.append(self.jsonpath)
        args.append("--output="+self.outputpath)
        args.extend(pdArgs)
        if pdFilters:
            f = ['--filter=' + x for x in pdFilters]
            args.extend(f)

        self.pandocRun(args)

        if self.debug: 
            print("STDERR: %s" % self.stderr)
            print("STDOUT: %s" % self.stdout)
        self.success = True

    def convertDocxToJson(self): 
        pdArgs = ['--smart', '--section-divs', '--atx-headers']
        if self.toc: 
            pdArgs.append('--toc')
        if self.format == "docx": 
            pdArgs.append('--extract-media=.')
        pdFilters = None
        pdMdOutFmt = 'json'

        args = [self.pandoc]
        args.append('--from=' + self.format)
        args.append('--to=' + pdMdOutFmt)
        args.append(self.inputpath)
        args.append("--output="+self.jsonpath)
        args.extend(pdArgs)
        if pdFilters:
            f = ['--filter=' + x for x in pdFilters]
            args.extend(f)

        self.pandocRun(args)

        if self.format == "docx": 
            self.mediafolder = os.path.join(self.outfolder, "media")
            if os.path.exists(self.mediafolder): 
                shutil.rmtree(self.mediafolder)
            if os.path.exists(os.path.join(self.cwd, "media")): 
                shutil.move(os.path.join(self.cwd, "media"), self.outfolder)
            else: 
                os.makedirs(os.path.join(self.outfolder, "media"))
            self.mediafolder = os.path.join(self.outfolder, "media")
        self.success = True

    def convertMdToHtml(self): 
        if not MARKDOWN: 
            warnings.warn("Install: pip install --user Markdown")
        else: 
            try: 
                mdexts = [
                    'markdown.extensions.admonition', 'markdown.extensions.attr_list', 
                    'markdown.extensions.def_list', 'markdown.extensions.footnotes', 
                    'markdown.extensions.meta', 'markdown.extensions.smarty', 
                    'markdown.extensions.tables', 'markdown.extensions.tables', 
                    'markdown.extensions.toc', 
                    'pymdownx.betterem', 'pymdownx.headeranchor', 'pymdownx.magiclink', 
                    'pymdownx.mark', 'pymdownx.superfences', 
                    'mdx_sections', 'markdown-figures.captions', 'markdown-wikilinks.gollum',
                     ]
                mdfile = codecs.open(self.outputpath, mode="r", encoding="utf-8")
                md = mdfile.read()
                html = markdown.markdown(md, extensions=mdexts)
                htmlfile = codecs.open(os.path.splitext(self.outputpath)[0] + ".html", 
                    "w", encoding="utf-8", errors="xmlcharrefreplace")
                htmlfile.write(html)
                htmlfile.close()
                self.success = True
            except: 
                self.success = False

    def convertDocxToMd(self): 
        # For various reasons, we run pandoc twice: 
        # Once docx-to-json, then json-to-md
        self.preparePaths()
        if self.success: 
            self.convertDocxToJson()
        if self.success: 
            self.prepareMedia()
        if self.success: 
            self.convertJsonToMd() 
        if self.success and self.html: 
            self.convertMdToHtml()
        if not self.debug: 
            try: 
                os.remove(self.jsonpath)
                os.remove(self.mediainfopath)
                shutil.rmtree(self.mediafolder)
            except: 
                warnings.warn("Cannot clean up!")

def parseOptions(): 
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputpath", help="input.docx file")
    parser.add_argument("outputpath", nargs='?', default=None, help="output.md file, default to input.md")
    parser.add_argument("-d", "--out-dir", help="output folder, default to current", action="store", default=None)
    parser.add_argument("-f", "--format", help="input format, default 'docx'", action="store", default='docx')
    parser.add_argument("-t", "--toc", help="generate TOC", action="store_true", default=False)
    parser.add_argument("-k", "--keep-dimensions", help="write image height and width into .md", action="store_true", default=False)
    parser.add_argument("-H", "--html", help="generate HTML from Markdown", action="store_true", default=False)
    parser.add_argument("-D", "--debug", help="keep intermediate files", action="store_true", default=False)
    parser.add_argument("--pandoc", help="path to 'pandoc' executable", default="/usr/local/bin/pandoc")
    parser.add_argument("--wmf2svg", help="path to 'wmf2svg.jar'", default="/usr/local/java/wmf2svg.jar")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument('-V', '--version', action='version', version="%(prog)s ("+__version__+")")
    args = parser.parse_args()
    return vars(args)

def main(): 
    opts = parseOptions()
    if opts["debug"]: 
        print("Running with options: %s" % opts)
    converter = DocxToMdConverter(**opts)
    converter.convertDocxToMd()
    if converter.success:
        if opts["verbose"]:  
            print("Done.")
    else: 
        if opts["verbose"]:  
            print("Nothing converted.")
        sys.exit(2)

if __name__ == '__main__':
    main()
