#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""wmftosvgpng 
  WMF to SVG or PNG converter
  Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
  https://github.com/twardoch/markdown-utils

Usage in shell: 
  $ wmftosvgpng.py -v -c -o vectorout vectorin.wmf
  ["svg", "./vectorout.svg"]
  $ wmftosvgpng.py -v -c -o bitmapout bitmapin.wmf
  ["png", "./bitmapout.png"]

Usage in Python:
  from mdutils import wmftosvgpng
  outputtype, outputpath = wmftosvgpng.toSvgOrPng(**{
      'inputpath': 'vectorin.wmf', 'outputbase': 'vectorout', 
      'compress': True, 'verbose': True, 'remove': True, 
      'wmf2svg': '/usr/local/java/wmf2svg.jar'
  })
"""

__version__ = "0.4.0"

import os
import sys
import subprocess
import argparse
import base64
import json
import xml.dom.minidom
import warnings
try: 
    import scour.scour
except ImportError: 
    pass

def optimizeSvg(svg): 
    try: 
        scopts = {'verbose': False, 'strip_ids': True, 'shorten_ids': True, 'simple_colors': True, 'strip_comments': True, 'error_on_flowtext': False, 'remove_metadata': True, 'remove_titles': True, 'outfilename': None, 'group_create': True, 'protect_ids_noninkscape': False, 'indent_type': 'space', 'newlines': True, 'keep_editor_data': False, 'shorten_ids_prefix': '', 'indent_depth': 1, 'keep_defs': False, 'renderer_workaround': True, 'remove_descriptions': True, 'style_to_xml': True, 'protect_ids_prefix': None, 'enable_viewboxing': True, 'digits': 5, 'embed_rasters': True, 'infilename': None, 'strip_xml_prolog': False, 'group_collapse': True, 'quiet': False, 'remove_descriptive_elements': False, 'strip_xml_space_attribute': False, 'protect_ids_list': None}
        svg = scour.scour.scourString(svg, scopts).encode("utf-8")
    except: 
        warnings.warn("scour not installed, run: pip install --user scour")
    return svg

def getPngOrSvg(svg): 
    try: 
        doc = xml.dom.minidom.parseString(svg)
        root = doc.documentElement
        if len(root.getElementsByTagName("image")) == 1 and len(root.getElementsByTagName("polygon")) + len(root.getElementsByTagName("path")) + len(root.getElementsByTagName("polyline")) == 0: 
            png64 = root.getElementsByTagName("image")[0].getAttribute("xlink:href")
            png = base64.decodestring(png64[22:])
            return True, png
        else: 
            for node in doc.getElementsByTagName("svg"): 
                node.setAttribute("height", "")
                node.removeAttribute("height")
                node.setAttribute("width", "")
                node.removeAttribute("width")
                node.setAttribute("preserveAspectRatio", "xMidYMid meet")
            return False, doc.toxml()
    except: 
        warnings.warn("Cannot analyze SVG!")
        return False, svg

def toSvg(**opts): 
    inputpath = os.path.realpath(opts["inputpath"])
    outputpath = os.path.realpath(opts["outputbase"] + ".svg")
    if not os.path.exists(inputpath): 
        return (False, "No file: %s" % (inputpath))
    else: 
        args = ["java", "-Djava.awt.headless=true", "-jar", opts["wmf2svg"], inputpath, outputpath]
        p = subprocess.Popen(args, bufsize=4096, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(None)
        if stderr or p.returncode: 
            return (False, stderr)
        else: 
            return (True, None)

def toSvgOrPng(**opts):
    success, err = toSvg(**opts)
    if err: 
        warnings.warn(err)
        return (None, None)
    svg = file(opts["outputbase"] + ".svg").read()
    isPng, buffer = getPngOrSvg(svg)
    returntype = None
    returnpath = None
    if isPng: 
        returntype = ".png"
        returnpath = os.path.realpath(opts["outputbase"] + returntype)
        outfile = file(returnpath, "wb")
        outfile.write(buffer)
        outfile.close()
        os.remove(opts["outputbase"] + ".svg")
    else: 
        if opts["compress"]: 
            svg = optimizeSvg(svg)
        returntype = ".svg"
        returnpath = os.path.realpath(opts["outputbase"] + returntype)
        outfile = file(returnpath, "w")
        outfile.write(buffer)
        outfile.close()
    if opts["remove"] and returntype and returnpath: 
        try: 
            os.remove(opts["inputpath"])
        except: 
            warnings.warn("Cannot remove %s" % (opts["inputpath"]))
    if opts["verbose"]: 
        print(json.dumps((returntype, returnpath)))
    return (returntype, returnpath)

def parseOptions(): 
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputpath", help="input.wmf file")
    parser.add_argument("outputbase", nargs='?', default=None, help="output base filename, defaults to input[.svg|.png]")
    parser.add_argument("-c", "--compress", action="store_true", default=False, help="compress SVG")
    parser.add_argument("-r", "--remove", action="store_true", default=False, help="remove input.wmf after conversion")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="report written file type and path")
    parser.add_argument("--wmf2svg", help="path to 'wmf2svg.jar'", default="/usr/local/java/wmf2svg.jar")
    parser.add_argument('-V', '--version', action='version', version="%(prog)s ("+__version__+")")
    args = vars(parser.parse_args())
    if not args["outputbase"]: 
        args["outputbase"] = os.path.splitext(args["inputpath"])[0]
    return args

def main(): 
    return toSvgOrPng(**parseOptions())

if __name__ == '__main__':
    main()
