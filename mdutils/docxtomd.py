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

changes:
  2017-10-25: Fixes
  2017-07-13: Added support for BMP output via PIL/Pillow

todo:
  * Add support for EMF
"""

__version__ = "0.4.5"

import argparse
import codecs
import fnmatch
import json
import os
import os.path
import shutil
import string
import subprocess
import sys
import warnings

import wmftosvgpng

try:
    import PIL.BmpImagePlugin
except ImportError:
    print("PIL or Pillow not found, run: pip install --user Pillow")
    sys.exit(2)

try:
    import markdown

    MARKDOWN = True
except ImportError:
    MARKDOWN = False


def extractAlphanumeric(InputString):
    return "".join([ch for ch in InputString if ch in (string.ascii_letters + string.digits)])


class DocxToMdConverter(object):
    def __init__(self, **opts):
        """
        Args:
            **opts ():
        """
        self.inputpath = opts.get("inputpath", None)
        self.outputpath = opts.get("outputpath", None)
        self.outfolder = opts.get("out_dir", None)
        self.format = opts.get("format", "docx")
        self.toc = opts.get("toc", False)
        self.pandoc = opts.get("with_pandoc", "/usr/local/bin/pandoc")
        self.wmf2svg = opts.get("with_wmf2svg", "/usr/local/java/wmf2svg.jar")
        self.verbose = opts.get("verbose", False)
        self.debug = opts.get("debug", False)
        self.jsonpath = opts.get("jsonpath", None)
        self.imgfolder = opts.get("img_dir", None)
        self.html = opts.get("html", False)
        self.keepimgdims = opts.get("keep_imgdims", False)
        self.recalcimgdims = opts.get("recalc_imgdims", False)
        self.recalcmaxdims = opts.get("recalc_maxdims", 500)
        self.success = True
        self.stdout = None
        self.stderr = None
        self.mediafolder = self.imgfolder
        self.cwd = os.path.dirname(os.path.realpath(os.getcwd()))
        self.mediainfopath = None

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
        self.mediaprefix = extractAlphanumeric(os.path.splitext(os.path.basename(self.outputpath))[0])
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
        p = subprocess.Popen(
            args, bufsize=4096, stdin=None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=new_env, cwd=self.cwd
        )
        if not p.returncode is None:
            raise RuntimeError(
                'Pandoc died with exitcode "%s" before receiving input: %s' % (
                    p.returncode, p.stderr.read())
            )
        try:
            self.stdout, self.stderr = p.communicate(None)
            self.success = True
        except OSError:
            self.success = False
            raise RuntimeError('Pandoc died with exitcode "%s" during conversion.' % (p.returncode))
        assert self.stdout == ""

    def prepareMedia(self):
        self.mediamap = {}
        if self.mediafolder: 
            for bmpfn in fnmatch.filter(os.listdir(self.mediafolder), '*.bmp'):
                fullsrc = os.path.join(self.mediafolder, bmpfn)
                fullout = os.path.splitext(fullsrc)[0] + '.png'
                pngfn = os.path.splitext(bmpfn)[0] + '.png'
                PIL.BmpImagePlugin.DibImageFile(fullsrc).save(fullout)
                self.mediamap[bmpfn] = pngfn

            for pngfn in fnmatch.filter(os.listdir(self.mediafolder), '*.png'):
                self.mediamap[pngfn] = pngfn

            for wmffn in fnmatch.filter(os.listdir(self.mediafolder), '*.wmf'):
                fullsrc = os.path.join(self.mediafolder, wmffn)
                fulloutbase = os.path.splitext(fullsrc)[0]
                rettype, retpath = wmftosvgpng.toSvgOrPng(**{
                    'inputpath' : fullsrc,
                    'outputbase': fulloutbase,
                    'compress'  : False,
                    'verbose'   : False,
                    'remove'    : not self.debug,
                    'wmf2svg'   : self.wmf2svg,
                })
                if rettype:
                    retfn = os.path.basename(retpath)
                    self.mediamap[wmffn] = retfn
            self.mediainfopath = os.path.join(self.outfolder, self.mediaprefix + ".media.json")
            mediainfofile = file(self.mediainfopath, "w")
            json.dump({
                "srcfull"  : self.mediafolder,
                "dstfull"  : self.imgfolder,
                "prefix"   : self.mediaprefix,
                "srcsubstr": u"./media/",
                "dstsubstr": u"img/",
                "map"      : self.mediamap
            }, mediainfofile)
            mediainfofile.close()
            os.environ['pandoc_filter_mapmedia'] = self.mediainfopath
            os.environ['pandoc_filter_keepimgdims'] = '1' if self.keepimgdims else '0'
            os.environ['pandoc_filter_recalcimgdims'] = '1' if self.recalcimgdims else '0'
            os.environ['pandoc_filter_recalcmaxdims'] = str(self.recalcmaxdims)

    def convertJsonToMd(self):
        pdArgs = [
            '--smart', '--section-divs', '--atx-headers', '--normalize'
        ]
        if self.toc:
            pdArgs.append('--toc')

        pdFilters = [
            os.path.join(os.path.dirname(__file__), 'pandoc_mapmedia.py'),
            os.path.join(os.path.dirname(__file__), 'pandoc_addimgdims.py'),
        ]

        pdMdExt = [
            '+angle_brackets_escapable', '+ascii_identifiers', '+auto_identifiers',
            '+autolink_bare_uris', '+backtick_code_blocks', '+blank_before_blockquote',
            '+blank_before_header', '+bracketed_spans', '+definition_lists', '+emoji',
            '+escaped_line_breaks', '+fenced_code_attributes', '+fenced_code_blocks',
            '+footnotes', '+hard_line_breaks', '+header_attributes', '+implicit_figures',
            '+implicit_header_references', '+intraword_underscores', '+line_blocks',
            '+link_attributes', '+pandoc_title_block', '+pipe_tables', '+raw_html',
            '+shortcut_reference_links', '+strikeout'
        ]
        pdMdOutFmt = 'markdown_github' + ''.join(pdMdExt)

        args = [self.pandoc]
        args.append('--from=' + 'json')
        args.append('--to=' + pdMdOutFmt)
        args.append(self.jsonpath)
        args.append("--output=" + self.outputpath)
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
        pdArgs = [
            '--smart', '--section-divs', '--atx-headers'
        ]
        if self.toc:
            pdArgs.append('--toc')
        if self.format == "docx":
            pdArgs.append('--extract-media=.')
        pdFilters = []
        pdMdOutFmt = 'json'

        args = [self.pandoc]
        args.append('--from=' + self.format)
        args.append('--to=' + pdMdOutFmt)
        args.append(self.inputpath)
        args.append("--output=" + self.jsonpath)
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
            warnings.warn("Install: pip install --user markdown")
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
                    'mdx_sections', 'figcap', 'mdx_steroids.wikilink',
                ]
                mdfile = codecs.open(self.outputpath, mode="r", encoding="utf-8")
                md = mdfile.read()
                html = markdown.markdown(md, extensions=mdexts)
                htmlfile = codecs.open(
                    os.path.splitext(self.outputpath)[0] + ".html",
                    "w", encoding="utf-8", errors="xmlcharrefreplace"
                )
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
            if self.jsonpath: 
                try:
                    os.remove(self.jsonpath)
                except:
                    warnings.warn("Cannot clean up %s" % (self.jsonpath))
            if self.mediainfopath: 
                try:
                    os.remove(self.mediainfopath)
                except:
                    warnings.warn("Cannot clean up %s" % (self.mediainfopath))
            if self.mediafolder: 
                try:
                    shutil.rmtree(self.mediafolder)
                except:
                    warnings.warn("Cannot clean up %s" % (self.mediafolder))


def parseOptions():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    grInput = parser.add_argument_group('input and output options')
    grInput.add_argument("inputpath", help="input.docx file")
    grInput.add_argument("-f", "--format", action="store", default='docx',
                         help="input format, default 'docx'")
    grInput.add_argument("outputpath", nargs='?', default=None,
                         help="output.md file, default to input.md")
    grInput.add_argument("-d", "--out-dir", action="store", default=None,
                         help="output folder, default to current")
    grProc = parser.add_argument_group('conversion options')
    grProc.add_argument("-t", "--toc", action="store_true", default=False,
                        help="generate TOC")
    grProc.add_argument("-k", "--keep-imgdims", action="store_true", default=False,
                        help="keep original image height and width")
    grProc.add_argument("-I", "--recalc-imgdims", action="store_true", default=False,
                        help="recalculate image px height and width")
    grProc.add_argument("-M", "--recalc-maxdims", action="store", type=int, default=500, 
                        help="max image width in px, otherwise 100%%, default: 500")
    grOutput = parser.add_argument_group('additional conversion options')
    grOutput.add_argument("-H", "--html", action="store_true", default=False,
                          help="also generate HTML from Markdown")
    grOther = parser.add_argument_group('other options')
    grOther.add_argument('-V', '--version', action='version', version="%(prog)s (" + __version__ + ")")
    grOther.add_argument("-D", "--debug", action="store_true", default=False,
                         help="keep intermediate files")
    grOther.add_argument("-v", "--verbose", action="store_true",
                         help="increase output verbosity")
    grOther.add_argument("--with-pandoc", default="/usr/local/bin/pandoc",
                         help="path to 'pandoc' binary")
    grOther.add_argument("--with-wmf2svg", default="/usr/local/java/wmf2svg.jar",
                         help="path to 'wmf2svg.jar' binary")
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
