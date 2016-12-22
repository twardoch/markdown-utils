#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pandoc filter to aid conversion of WMF files to SVG or PNG.

  Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
  https://github.com/twardoch/markdown-utils

  * Python skeleton for Image filter:
    ```python
    def function(key, value, format, meta):
        format = 'markdown'
        meta = {}
        if key == u'Image':
            attrs, alt, [src, title] = value
            attrs = [u'imgid', [u'imgclass', u'imgclass2'], [[u'attr1', u'val1'], [u'attr2', u'val2']]]
            alt = [{u'c': u'altword1', u't': u'Str'}, {u't': u'Space'}, {u'c': u'altword2', u't': u'Str'}]
            src = u'pathtoimg'
            title = u'title'
            return Image(attrs, alt, [src, title])

    if __name__ == "__main__":
        toJSONFilter(pandoc_addimgdims)
    ```
  * JSON representation:
    ```json
    { "t":"Image", "c":
        [
            [ "imgid",
                [ "imgclass", "imgclass2" ],
                [
                    ["attr1","val1"],["attr2","val2"]
                ]
            ],
            [
                {"t":"Str","c":"altword1"},{"t":"Space"},{"t":"Str","c":"altword2"}
            ],
            [ "pathtoimg", "title" ]
        ]
    }
    ```
  * Markdown representation:
    ```markdown
    ![altword1 altword2](pathtoimg){#imgid .imgclass .imgclass2 attr1="val1" attr2="val2"}
    ```
"""

__version__ = "0.4.4"

import json
import os
import shutil
import string
import sys

from pandocfilters import Image, Str, stringify, toJSONFilter


def pprint(s):
    sys.stderr.write(unicode(s).encode('utf-8'))
    sys.stderr.write(u"\n".encode('utf-8'))
    sys.stderr.flush()


def ExtractAlphanumeric(InputString):
    return "".join([ch for ch in InputString if ch in (string.ascii_letters + string.digits)])


def pandoc_wmftosvgpng(key, value, format, meta):
    """
    Args:
        key ():
        value ():
        format ():
        meta ():

    Returns:
        pandocfilters.Image()
    """
    if key == 'Image':
        attrs, alt, [src, title] = value

        mediainfopath = os.environ.get('pandoc_filter_mapmedia', None)
        if not mediainfopath:
            return Image(attrs, alt, [src, title])

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
        altstr = ""
        if alt:
            altstr = stringify(alt)
            altstr = ExtractAlphanumeric(altstr)[-30:]
            suffix = "_" + altstr

        dstfn = prefix + "_" + newbase + suffix + dstext

        if altstr:
            altstr = prefix + "_" + altstr
        else:
            altstr = prefix + "_" + newbase
        alt = [Str(altstr)]
        if not title:
            title = unicode(altstr)

        newsrc = os.path.join(dstsubstr, dstfn)
        srcpath = os.path.join(srcfolder, mapfn)
        dstpath = os.path.join(dstfolder, dstfn)

        if os.path.exists(dstpath):
            os.remove(dstpath)
        shutil.copyfile(srcpath, dstpath)

        src = unicode(newsrc)

        return Image(attrs, alt, [src, title])


if __name__ == '__main__':
    toJSONFilter(pandoc_wmftosvgpng)
