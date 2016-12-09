# docxtomd.sh
Hacky script to convert a Word .docx to Markdown

[Pandoc](http://pandoc.org/) converts `.docx` to `.md` well but only extracts media which can be `.png` or `.wmf`, and links them inside the `.md` file.

But `.wmf` files need to be converted to something else, `.svg` or `.png`. In this implementation, I use a Java workflow ([`wmf2svg`](https://github.com/hidekatsu-izuno/wmf2svg) and [`batik`](https://xmlgraphics.apache.org/batik/)) first because many `.wmf` are actually bitmap images, so they’re best ultimately converted to `.png`. When that workflow fails, I use the [`libwmf`](http://wvware.sourceforge.net/libwmf.html) tool which does well
vectors but not bitmaps.  

# Requirements 

* perl, bash, Mac OS X
* [pandoc](http://pandoc.org/installing.html)
* Java [wmf2svg](https://github.com/hidekatsu-izuno/wmf2svg) — build with `ant`, unzip, move `wmf2svg-0.9.8.jar` to `/usr/local/java`
* Java [batik](https://xmlgraphics.apache.org/batik/download.html) — place `batik` folder in `/usr/local/java`
* [`libwmf wmf2svg`](http://wvware.sourceforge.net/libwmf.html) — `brew install libwmf`

# Usage

If your file is `mydoc.docx`, run `docxtomd.sh mydoc`

# License
Copyright (c) 2016 by Adam Twardoch
[https://github.com/twardoch/markdown-utils](https://github.com/twardoch/markdown-utils)
Licensed under Apache 2.0
