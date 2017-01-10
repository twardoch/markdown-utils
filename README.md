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
* [wmf2svg](https://github.com/hidekatsu-izuno/wmf2svg) — build with 'ant'

Then run:
```
pip install --user --process-dependency-links git+https://github.com/twardoch/markdown-utils.git
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
usage: docxtomd [-h] [-f FORMAT] [-d OUT_DIR] [-t] [-k] [-I] [-H] [-V] [-D]
                [-v] [--with-pandoc WITH_PANDOC] [--with-wmf2svg WITH_WMF2SVG]
                inputpath [outputpath]

docxtomd
  Word .docx to Markdown converter
  Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
  https://github.com/twardoch/markdown-utils

This tool converts a Word .docx file to Markdown using pandoc.
Unlike pandoc, it intelligently converts and names the vector
or bitmap images contained in the .docx into either .svg or .png.

example:
  $ ./docxtomd.py --html -d test/test1 test/test1.docx

optional arguments:
  -h, --help            show this help message and exit

input and output options:
  inputpath             input.docx file
  -f FORMAT, --format FORMAT
                        input format, default 'docx'
  outputpath            output.md file, default to input.md
  -d OUT_DIR, --out-dir OUT_DIR
                        output folder, default to current

conversion options:
  -t, --toc             generate TOC
  -k, --keep-imgdims    keep original image height and width
  -I, --recalc-imgdims  recalculate image height and width

additional conversion options:
  -H, --html            also generate HTML from Markdown

other options:
  -V, --version         show program's version number and exit
  -D, --debug           keep intermediate files
  -v, --verbose         increase output verbosity
  --with-pandoc WITH_PANDOC
                        path to 'pandoc' binary
  --with-wmf2svg WITH_WMF2SVG
                        path to 'wmf2svg.jar' binary
```

## wmftosvgpng

WMF to SVG or PNG converter

* Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
* https://github.com/twardoch/markdown-utils

### Requires

* Java wmf2svg: https://github.com/hidekatsu-izuno/wmf2svg — build with 'ant', unzip, move wmf2svg-0.9.8.jar to /usr/local/java

* (optional) scour: https://github.com/scour-project/scour/
```
pip install --user scour
```

### Usage

```
usage: wmftosvgpng [-h] [-c] [-r] [-v] [-V] [--with-wmf2svg WITH_WMF2SVG]
                   inputpath [outputbase]

wmftosvgpng
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
      'with_wmf2svg': '/usr/local/java/wmf2svg.jar'
  })

positional arguments:
  inputpath             input.wmf file
  outputbase            output base filename, defaults to input[.svg|.png]

optional arguments:
  -h, --help            show this help message and exit
  -c, --compress        compress SVG
  -r, --remove          remove input.wmf after conversion
  -v, --verbose         report written file type and path
  -V, --version         show program's version number and exit
  --with-wmf2svg WITH_WMF2SVG
                        path to 'wmf2svg.jar' binary
```


### Projects related to Markdown and MkDocs by Adam Twardoch: 

* [https://twardoch.github.io/markdown-rundown/](https://twardoch.github.io/markdown-rundown/) — summary of Markdown formatting styles [git](https://github.com/twardoch/markdown-rundown)
* [https://twardoch.github.io/markdown-utils/](https://twardoch.github.io/markdown-utils/) — various utilities for working with Markdown-based documents [git](https://github.com/twardoch/markdown-utils)
* [https://twardoch.github.io/mkdocs-combine/](https://twardoch.github.io/mkdocs-combine/) — convert an MkDocs Markdown source site to a single Markdown document [git](https://github.com/twardoch/mkdocs-combine)
* [https://github.com/twardoch/noto-mkdocs-theme/tree/rework](https://github.com/twardoch/noto-mkdocs-theme/tree/rework) — great Material Design-inspired theme for MkDocs [git](https://github.com/twardoch/noto-mkdocs-theme)
* [https://twardoch.github.io/clinker-mktheme/](https://twardoch.github.io/clinker-mktheme/) — great theme for MkDocs [git](https://github.com/twardoch/clinker-mktheme)
