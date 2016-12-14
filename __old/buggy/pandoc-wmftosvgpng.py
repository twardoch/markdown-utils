#! /usr/bin/env python
"""
Pandoc filter to convert WMF files to SVG or PNG.
Inspired by: 
https://gist.github.com/jeromerobert/3996eca3acd12e4c3d40
"""

__author__ = "Adam Twardoch"

import os
import sys
import subprocess
import mimetypes
import shutil
from string import ascii_letters, digits
from pandocfilters import toJSONFilter, Str, Para, Image
import wmftosvgpng

def pprint(s): 
    sys.stderr.write(unicode(s).encode('utf-8'))
    sys.stderr.write(u"\n".encode('utf-8'))
    sys.stderr.flush()

def ExtractAlphanumeric(InputString):
    return "".join([ch for ch in InputString if ch in (ascii_letters + digits)])

def pandoc_wmftosvgpng(key, value, fmt, meta):
    if key == 'Image':
        if len(value) == 2:
            # before pandoc 1.16
            alt, [src, title] = value
            attrs = None
        else:
            attrs, alt, [src, title] = value

        oldsrc = src
        mdfolder = os.environ['pandoc_wmftosvgpng']
        fullmdfolder = os.path.normpath(os.path.realpath(mdfolder))
        fullsrc = os.path.normpath(os.path.realpath(os.path.join(fullmdfolder, src)))
        if sys.platform == 'win32':
            pathels = fullsrc.split("\\")
        else: 
            pathels = fullsrc.split("/")
        prefixfn = pathels[-3]
        outfolder = os.path.join(mdfolder, "img")
        fulloutfolder = os.path.join(fullmdfolder, "img")

        outbasefn = os.path.splitext(os.path.split(src)[1])[0]
        if alt: 
            if len(alt) > 0: 
                outbasefn = ExtractAlphanumeric(alt[0]['c'])
        outbasefn = prefixfn + "_" + outbasefn
        outbase = os.path.join(outfolder, outbasefn)

        fulloutbase = os.path.join(fulloutfolder, outbasefn)

        srctype = str(os.path.splitext(src)[1].lower())

        newsrcbase = os.path.join("img", outbasefn)
        fullnewsrcbase = os.path.join(fullmdfolder, newsrcbase)

        mtime = 0
        try:
            mtime += os.path.getmtime(fullnewsrcbase + ".png")
        except OSError:
            mtime += 0
        try:
            mtime += os.path.getmtime(fullnewsrcbase + ".svg")
        except OSError:
            mtime += 0

        if mtime < os.path.getmtime(fullsrc):
            newsrc = newsrcbase + srctype
            fullnewsrc = fullnewsrcbase + srctype

            if srctype == ".wmf": 
                rettype, retpath = wmftosvgpng.toSvgOrPng(**{
                    'inputpath': fullsrc, 'outputbase': fulloutbase, 
                    'compress': False, 'verbose': True, 'remove': False, 
                    'wmf2svg': '/usr/local/java/wmf2svg-0.9.8.jar'
                })
                if rettype: 
                    newsrc = newsrcbase + rettype
                    fullnewsrc = fullnewsrcbase + rettype
                #pprint("%s: %s" % (rettype, retpath))
                #pprint("%s: %s" % (src, newsrc))
                #pprint("")
            else: 
                shutil.copyfile(fullsrc, fullnewsrc)

            while True: 
                if os.path.exists(fullnewsrc): 
                    break

            src = unicode(newsrc)

        if attrs:
            return Image(attrs, alt, [src, title])
        else:
            return Image(alt, [src, title])


if __name__ == "__main__":
    toJSONFilter(pandoc_wmftosvgpng)
