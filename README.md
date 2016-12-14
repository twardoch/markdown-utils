# mdutils

Python package for working with Markdown. Includes `docxtomd`, a Word .docx to Markdown converted using `pandoc` and `wmf2svg`, and `wmftosvgpng`, an intelligent WMF to SVG or PNG converter using `wmf2svg`.

* Copyright (c) 2016 by Adam Twardoch
* Licensed under Apache 2.0.
* [https://github.com/twardoch/markdown-utils](https://github.com/twardoch/markdown-utils)

## Installation

On Mac OS X, install [Homebrew](http://brew.sh/) and then in Terminal run:
```
./install-mac.sh
```

On other systems, install the dependencies:
* [pandoc](http://pandoc.org/)
* [wmf2svg](https://github.com/hidekatsu-izuno/wmf2svg) — build with 'ant'

Then run:
```
pip install --user git+https://github.com/twardoch/markdown-utils.git
```

## docxtomd

Utility for Word .docx to Markdown conversion using pandoc and wmf2svg

### Rationale

[Pandoc](http://pandoc.org/) converts `.docx` to `.md` well but only extracts
media which can be `.png` or `.wmf`, and links them inside the `.md` file.
Yet `.wmf` files need to be converted to something else, `.svg` or `.png`.

This implementation performs three steps:

1. Convert the `.docx` to `.doc.json` using Pandoc, extracting media.
2. Calls the `wmftosvgpng` tool on all extracted media. This tool uses a Java tool [`wmf2svg`](https://github.com/hidekatsu-izuno/wmf2svg) to convert `.wmf` into `.svg`, then parses the `.svg` and if the `.svg` only contains one embedded PNG bitmap, saves it as a plain `.png`. This also produces a `.media.json` file which contains some mapping between the old and the new files.
3. Convert from `.doc.json` to `.md` using Pandoc, calling the `pandoc-mapmedia.py` Pandoc filter, which (aided by `.media.json`) remaps the path references to the media files and renames those which have the `alt` attribute available. It also copies the new media files from the `media/` subfolder into the `img/` subfolder.

The result is a more robust Markdown file with extracted media. Optionally, the tool can also generate `.html` from the `.md` using the Python `Markdown` module.

### Usage

```
usage: docxtomd.py [-h] [-d OUT_DIR] [-f FORMAT] [-t] [-H] [--pandoc PANDOC]
                   [--wmf2svg WMF2SVG] [-v]
                   inputpath [outputpath]

docxtomd 0.2
  DOCX to Markdown converter
  Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
  https://github.com/twardoch/markdown-utils

example:
  $ ./docxtomd.py -v -d test/test1 test/test1.docx

positional arguments:
  inputpath             input.docx file
  outputpath            output.md file, default to input.md

optional arguments:
  -h, --help            show this help message and exit
  -d OUT_DIR, --out-dir OUT_DIR
                        output folder, default to current
  -f FORMAT, --format FORMAT
                        input format, default 'docx'
  -t, --toc             generate TOC
  -H, --html            generate HTML from Markdown
  --pandoc PANDOC       path to 'pandoc' executable
  --wmf2svg WMF2SVG     path to wmf2svg-n.n.n.jar
  -v, --verbose         increase output verbosity
```

## wmftosvgpng

WMF to SVG or PNG converter

* Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
* https://github.com/twardoch/markdown-utils

### Requires

* Java wmf2svg: https://github.com/hidekatsu-izuno/wmf2svg — build with 'ant', unzip, move wmf2svg-0.9.8.jar to /usr/local/java

* (optional) scour: https://github.com/scour-project/scour/
```
pip install --user scour
```

### Usage

Usage in shell:
```
usage: wmftosvgpng.py [-h] [-c] [-r] [-v] [--wmf2svg WMF2SVG]
                      inputpath [outputbase]
positional arguments:
  inputpath          input.wmf file
  outputbase         output base filename, defaults to input[.svg|.png]

optional arguments:
  -h, --help         show this help message and exit
  -c, --compress     compress SVG
  -r, --remove       remove input.wmf after conversion
  -v, --verbose      report written file type and path
  --wmf2svg WMF2SVG  path to wmf2svg-n.n.n.jar

examples:
  $ wmftosvgpng.py -v -c -o vectorout vectorin.wmf
  ["svg", "./vectorout.svg"]
  $ wmftosvgpng.py -v -c -o bitmapout bitmapin.wmf
  ["png", "./bitmapout.png"]
```

Usage in Python:
```
  import wmftosvgpng
  outputtype, outputpath = wmftosvgpng.toSvgOrPng(**{
      'inputpath': 'vectorin.wmf', 'outputbase': 'vectorout',
      'compress': True, 'verbose': True, 'remove': True,
      'wmf2svg': '/usr/local/java/wmf2svg-0.9.8.jar'
  })
```
