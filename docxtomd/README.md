# docxtomd.py

Utility for Word .docx to Markdown conversion using pandoc and wmf2svg

* Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
* https://github.com/twardoch/markdown-utils

### Rationale

[Pandoc](http://pandoc.org/) converts `.docx` to `.md` well but only extracts
media which can be `.png` or `.wmf`, and links them inside the `.md` file.
Yet `.wmf` files need to be converted to something else, `.svg` or `.png`.

This implementation performs three steps:

1. Convert the `.docx` to `.doc.json` using Pandoc, extracting media.
2. Calls the `wmftosvgpng` tool on all extracted media. This tool uses a Java tool [`wmf2svg`](https://github.com/hidekatsu-izuno/wmf2svg) to convert `.wmf` into `.svg`, then parses the `.svg` and if the `.svg` only contains one embedded PNG bitmap, saves it as a plain `.png`. This also produces a `.media.json` file which contains some mapping between the old and the new files.
2. Convert from `.doc.json` to `.md` using Pandoc, calling the `pandoc-mapmedia.py` Pandoc filter, which remaps the path references to the media files and renames those which have the `alt` attribute available. It also copies the new media files from the `media/` subfolder into the `img/` subfolder.

The result is a more robust Markdown file with extracted media.

### Usage

```
usage: docxtomd.py [-h] [-d OUT_DIR] [-f FORMAT] [-t] [-H] [--pandoc PANDOC]
                   [--wmf2svg WMF2SVG] [-v]
                   inputpath [outputpath]

docxtomd 0.2
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

# wmftosvgpng.py

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

# buggy/docxtomd.py

This is the old implementation which is buggy, reported in https://github.com/jgm/pandoc/issues/3313

During the 2nd conversion, `pandoc-wmftosvgpng.py` is called as a Pandoc filter. This calls the `wmftosvgpng` module which runs the Java-based `[wmf2svg](https://github.com/hidekatsu-izuno/wmf2svg)` tool. Something there screws up the Pandoc flow, so Pandoc finishes with an error:

```
$ ./docxtomd.py -v -d test/test1 test/test1.docx
Running: /usr/local/bin/pandoc --from=docx --to=json ./test/test1.docx --output=./test/test1/test1.md-tmp.json --smart --section-divs --atx-headers --extract-media=.
Running: /usr/local/bin/pandoc --from=json --to=markdown_github-pipe_tables+auto_identifiers+backtick_code_blocks+blank_before_blockquote+blank_before_header+bracketed_spans+definition_lists+escaped_line_breaks+fenced_code_attributes+footnotes+grid_tables+header_attributes+implicit_header_references+line_blocks+pandoc_title_block ./test/test1/test1.md-tmp.json --output=./test/test1/test1.md --smart --section-divs --atx-headers --filter=./pandoc-wmftosvgpng.py
.svg: ./test/test1/img/image2.svg
./media/image2.wmf: img/image2.svg

pandoc: Error in $: endOfInput
CallStack (from HasCallStack):
  error, called at pandoc.hs:144:42 in main:Main


Done.
```

# old/docxtomd.sh
`old/docxtomd.sh` is an old hacky shell script to convert a Word .docx to Markdown, a predecessor of `docxtomd.py`. It uses `pandoc` along with a  Java workflow ([`wmf2svg`](https://github.com/hidekatsu-izuno/wmf2svg) and [`batik`](https://xmlgraphics.apache.org/batik/)) first because many `.wmf` are actually bitmap images, so they’re best ultimately converted to `.png`. When that workflow fails, I use the [`libwmf`](http://wvware.sourceforge.net/libwmf.html) tool which does well
vectors but not bitmaps.

### Requirements

* perl, bash, Mac OS X
* [pandoc](http://pandoc.org/) — best install the Mac [prebuilt package](https://github.com/jgm/pandoc/releases/)
* Java [wmf2svg](https://github.com/hidekatsu-izuno/wmf2svg) — build with `ant`, unzip, move `wmf2svg-0.9.8.jar` to `/usr/local/java`
* Java [batik](https://xmlgraphics.apache.org/batik/download.html) — place `batik` folder in `/usr/local/java`
* [`libwmf wmf2svg`](http://wvware.sourceforge.net/libwmf.html) — `brew install libwmf`

### Usage

If your file is `mydoc.docx`, run `docxtomd.sh mydoc`

# License
Copyright (c) 2016 by Adam Twardoch [https://github.com/twardoch/markdown-utils](https://github.com/twardoch/markdown-utils).

Licensed under Apache 2.0.
