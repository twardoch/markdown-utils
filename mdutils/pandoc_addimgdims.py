#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Pandoc filter to add image dimensions to SVG or PNG.

> Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
> https://github.com/twardoch/markdown-utils

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
import sys
try:
    import PIL.Image
except:
    pprint("PIL or Pillow not found, run: pip install --user Pillow")

from pandocfilters import Image, toJSONFilter


def pprint(s):
    log = sys.stderr
    log.write(unicode(s).encode('utf-8'))
    log.write(u"\n".encode('utf-8'))
    log.flush()


def pandoc_addimgdims(key, value, format, meta):
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
        keepimgdims = True if os.environ.get('pandoc_filter_keepimgdims', '0') == '1' else False
        recalcimgdims = True if os.environ.get('pandoc_filter_recalcimgdims', '0') == '1' else False
        recalcmaxdims = os.environ.get('pandoc_filter_recalcmaxdims', '500')
        try:
            recalcmaxdims = int(recalcmaxdims)
        except ValueError:
            recalcmaxdims = 500
        mediainfopath = os.environ.get('pandoc_filter_mapmedia', None)
        attrs, alt, [src, title] = value
        if not mediainfopath:
            return Image(attrs, alt, [src, title])

        mediainfo = json.load(file(mediainfopath))
        dstfolder = mediainfo['dstfull']

        srcpath = os.path.join(dstfolder, os.path.split(src)[1])

        #if os.path.splitext(srcpath)[1].lower() == ".svg":
        #    pil = PIL.Image.open(srcpath)
        #    pprint("%s %s" % (src, pil.size))
        #    pprint(recalcmaxdims)
#
        #elif os.path.splitext(srcpath)[1].lower() == ".png":
        #    pil = PIL.Image.open(srcpath)
        #    pprint("%s %s" % (src, pil.size))
        #    pprint(recalcmaxdims)
#
        #pprint("key: %s" % repr(key))
        #pprint("attrs: %s" % repr(attrs))
        #pprint("alt: %s" % repr(alt))
        #pprint("src: %s" % repr(src))
        #pprint("title: %s" % repr(title))
        #pprint("format: %s" % repr(format))
        #pprint("meta: %s" % repr(meta))

        return Image(attrs, alt, [src, title])


if __name__ == "__main__":
    toJSONFilter(pandoc_addimgdims)
