# docxtomd

**OLD OR BUGGY VERSIONS**

Utility for Word .docx to Markdown conversion using pandoc and wmf2svg

* Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
* https://github.com/twardoch/markdown-utils

### Rationale

[Pandoc](http://pandoc.org/) converts `.docx` to `.md` well but only extracts
media which can be `.png` or `.wmf`, and links them inside the `.md` file.
Yet `.wmf` files need to be converted to something else, `.svg` or `.png`.

## buggy/docxtomd.py

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

## old/docxtomd.sh

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
