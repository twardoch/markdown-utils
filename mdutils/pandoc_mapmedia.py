#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pandoc filter to aid conversion of WMF files to SVG or PNG.

  Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
  https://github.com/twardoch/markdown-utils
"""

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

        mediainfopath = os.environ['pandoc_mapmedia']
        mediainfo = json.load(file(mediainfopath))
        srcfolder = mediainfo['srcfull']
        dstfolder = mediainfo['dstfull']
        srcsubstr = mediainfo['srcsubstr']
        dstsubstr = mediainfo['dstsubstr']
        mediamap = mediainfo['map']

        newsrc = src
        srcfn = os.path.basename(src)
        mapfn = mediamap.get(srcfn, srcfn)
        dstfn = mapfn

        dstbase, dstext = os.path.splitext(mapfn)
        prefix = mediainfo['prefix']
        newbase = dstbase[5:].zfill(4)
        suffix = ""
        if alt: 
            if len(alt) > 0: 
                suffix = "_" + ExtractAlphanumeric(alt[0]['c'])
        dstfn = prefix + "_" + newbase + suffix + dstext

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
