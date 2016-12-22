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

__version__ = "0.4.3"

import os
import sys

from pandocfilters import Image, toJSONFilter


def pprint(s):
    sys.stderr.write(unicode(s).encode('utf-8'))
    sys.stderr.write(u"\n".encode('utf-8'))
    sys.stderr.flush()


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
        attrs, alt, [src, title] = value

        if os.path.splitext(src)[1].lower() == ".svg":
            pass

        elif os.path.splitext(src)[1].lower() == ".png":
            pass

        pprint("key: %s" % repr(key))
        pprint("attrs: %s" % repr(attrs))
        pprint("alt: %s" % repr(alt))
        pprint("src: %s" % repr(src))
        pprint("title: %s" % repr(title))
        pprint("format: %s" % repr(format))
        pprint("meta: %s" % repr(meta))

        return Image(attrs, alt, [src, title])


if __name__ == "__main__":
    toJSONFilter(pandoc_addimgdims)
