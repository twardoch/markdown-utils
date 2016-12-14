#!/usr/bin/env sh
docxtomd --debug --toc --html -d test1 test1.docx
open test1/test1.html
