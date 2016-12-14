#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""docxtomd 0.1
  DOCX to Markdown converter
  Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
  https://github.com/twardoch/markdown-utils

Pandoc converts `.docx` to `.md` well but only extracts 
media which can be `.png` or `.wmf`, and links them inside the 
`.md` file. This tool converts the `.docx` to `.json`, 
then from `.json` to `.md`. The second step also intelligently 
converts `.wmf` into either `.svg` or `.png`. 
The result is a more robust Markdown file with extracted media. 

example: 
  $ ./docxtomd.py -v -d test/test1 test/test1.docx
"""

import os
import warnings
import sys
import os.path
import sh
import argparse
import subprocess
import shutil

class DocxToMdConverter(object): 

    def __init__(self, **opts):
        self.inputpath = opts.get("inputpath", None)
        self.outputpath = opts.get("outputpath", None)
        self.outfolder = opts.get("out_dir", None)
        self.format = opts.get("format", "docx")
        self.toc = opts.get("toc", False)
        self.pandoc = opts.get("pandoc", "/usr/local/bin/pandoc")
        self.verbose = opts.get("verbose", False)
        self.jsonpath = opts.get("jsonpath", None)
        self.imgfolder = opts.get("img_dir", None)
        self.success = True
        self.stdout = None
        self.stderr = None

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
            self.outputpath = os.path.join(self.outfolder, os.path.split(self.outputpath)[1])
        else: 
            self.outfolder = os.path.split(self.outputpath)[0]
        if not os.path.exists(self.outfolder): 
            try: 
                os.makedirs(self.outfolder)
            except: 
                warnings.warn("Cannot create folder %s" % (self.outfolder))
                self.success = False
        if not self.jsonpath: 
            self.jsonpath = self.outputpath + "-tmp.json"
        if not self.imgfolder: 
            self.imgfolder = os.path.join(self.outfolder, "img")
        if not os.path.exists(self.imgfolder): 
            try: 
                os.makedirs(self.imgfolder)
            except: 
                warnings.warn("Cannot create folder %s" % (self.imgfolder))
                self.success = False

    def pandocRun(self, args): 
        # To get access to pandoc-citeproc when we use a included copy of pandoc,
        # we need to add the pypandoc/files dir to the PATH
        new_env = os.environ.copy()
        cwd = os.path.dirname(os.path.realpath(__file__))
        files_path = os.path.join(cwd, "files")
        new_env["PATH"] = new_env.get("PATH", "") + os.pathsep + files_path

        if self.verbose: 
            print("Running: " + " ".join(args))
        p = subprocess.Popen(args, bufsize=4096, stdin=None, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=new_env, cwd=cwd)
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

    def convertJsonToMd(self): 
        pdArgs = ['--smart', '--section-divs', '--atx-headers']
        pdFilters = ['./pandoc-wmftosvgpng.py']
        os.environ['pandoc_wmftosvgpng'] = self.outfolder

        pdMdExt = ['-pipe_tables', '+auto_identifiers', '+backtick_code_blocks', '+blank_before_blockquote', '+blank_before_header', '+bracketed_spans', '+definition_lists', '+escaped_line_breaks', '+fenced_code_attributes', '+footnotes', '+grid_tables', '+header_attributes', '+implicit_header_references', '+line_blocks', '+pandoc_title_block']
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

        if self.verbose: 
            print(self.stderr)
            print(self.stdout)
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
            mediafolder = os.path.join(self.outfolder, "media")
            if os.path.exists(mediafolder): 
                shutil.rmtree(mediafolder)
            shutil.move("media", self.outfolder)
        self.success = True

    def convertDocxToMd(self): 
        # For various reasons, we run pandoc twice: 
        # Once docx-to-json, then json-to-md
        self.preparePaths()
        if self.success: 
            self.convertDocxToJson()
        if self.success: 
            self.convertJsonToMd() 

def parseOptions(): 
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputpath", help="input.docx file")
    parser.add_argument("outputpath", nargs='?', default=None, help="output.md file, default to input.md")
    parser.add_argument("-d", "--out-dir", help="output folder, default to current", action="store", default=None)
    parser.add_argument("-f", "--format", help="input format, default 'docx'", action="store", default='docx')
    parser.add_argument("-t", "--toc", help="generate TOC", action="store_true", default=False)
    parser.add_argument("--pandoc", help="path to 'pandoc' executable", default="/usr/local/bin/pandoc")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    args = parser.parse_args()
    return vars(args)

def main(): 
    opts = parseOptions()
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
