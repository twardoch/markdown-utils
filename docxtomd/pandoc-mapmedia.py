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
import string
import json
from pandocfilters import toJSONFilter, Str, Para, Image

def pprint(s): 
    sys.stderr.write(unicode(s).encode('utf-8'))
    sys.stderr.write(u"\n".encode('utf-8'))
    sys.stderr.flush()

def ExtractAlphanumeric(InputString):
    return "".join([ch for ch in InputString if ch in (string.ascii_letters + string.digits)])

def pandoc_wmftosvgpng(key, value, fmt, meta):
    if key == 'Image':
        if len(value) == 2:
            # before pandoc 1.16
            alt, [src, title] = value
            attrs = None
        else:
            attrs, alt, [src, title] = value

        mediainfopath = os.environ['pandoc_mediainfo']
        mediainfo = json.load(file(mediainfopath))
        srcfolder = mediainfo['srcfull']
        dstfolder = mediainfo['dstfull']
        prefix = mediainfo['prefix']
        srcsubstr = mediainfo['srcsubstr']
        dstsubstr = mediainfo['dstsubstr']
        mediamap = mediainfo['map']

        newsrc = src
        srcfn = os.path.basename(src)
        mapfn = mediamap.get(srcfn, srcfn)
        dstfn = mapfn
        if alt: 
            if len(alt) > 0: 
                dstfn = ExtractAlphanumeric(alt[0]['c']) + os.path.splitext(dstfn)[1]
        dstfn = prefix + "_" + dstfn
        newsrc = os.path.join(dstsubstr, dstfn)
        srcpath = os.path.join(srcfolder, mapfn)
        dstpath = os.path.join(dstfolder, dstfn)
        if os.path.exists(dstpath): 
            os.remove(dstpath)
        shutil.copyfile(srcpath, dstpath)

        src = unicode(newsrc)

        if attrs:
            return Image(attrs, alt, [src, title])
        else:
            return Image(alt, [src, title])


if __name__ == "__main__":
    toJSONFilter(pandoc_wmftosvgpng)
