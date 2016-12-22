#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
THIS IS UNDER DEVELOPMENT
"""

import argparse
import os
import re


# Main function
def main(args):
    docname = args.get("inpath", None)
    docfile = file(docname)
    maintext = docfile.readlines()
    if len(maintext) == 0:
        print("Document is Empty!")
        return
    source_dir = os.path.split(docname)[0]
    file_dir = os.path.splitext(docname)[0]
    make_groups = int(args.get("groups"))
    levels = str(args.get("levels"))

    links = {}
    textlines = extract_links(maintext, links)
    split_file(file_dir, textlines, make_groups, levels, links)


# Extract all end of page links and footnotes, and store them in dict for
# lookup


def extract_links(maintext, links):
    textlines = []
    for line in maintext:
        m = re.match('(\[.+?\]):.*', line)
        if m:
            key = m.group(1)
            links[key] = line
        else:
            textlines.append(line)
    return textlines


# Split .md file on h1 and h2 (#, ##) sections, option for grouping in sub
# dirs on h1
def split_file(file_dir, textlines, make_groups, levels, links):
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    section = []
    out_dir = file_dir
    sub_dir = file_dir
    gr1, gr2 = '', ''
    findex = 0
    grindex = 0
    ml = ("index",)
    for line in textlines:
        m = re.match('#[^#](.*)', line)
        if m and make_groups > 0:
            grindex += 1
            ml = m.groups()
            gr1 = make_group(ml, grindex)
            gr2 = ''
            sub_dir = os.path.join(file_dir, gr1)
            os.makedirs(sub_dir)

        m2 = re.match('##[^#](.*)', line)
        if m2 and make_groups == 2:
            grindex += 1
            ml2 = m2.groups()
            gr2 = make_group(ml2, grindex)
            sub_dir = os.path.join(file_dir, gr1, gr2)
            os.makedirs(sub_dir)

        if re.match('#{1,' + levels + '}[^#]', line):
            if len(section) > 0:
                ml = ("index",)
                if m2:
                    ml = m2.groups()
                elif m:
                    ml = m.groups()
                writefile(out_dir, ml, findex, '\n'.join(section), links)
            section = []
            findex += 1
            out_dir = sub_dir
        section.append(line)
    # write last section (or complete doc, if no sections)
    if len(section) > 0:
        writefile(out_dir, ml, findex, '\n'.join(section), links)


def make_group(ml, index):
    title = ml[0].strip()
    title = re.sub(r'<.*?>', '', title)
    title = re.sub(r'[*_/\\:."\'+$><|]', '', title)
    title = re.sub(r'–—•', '-', title)
    title = re.sub(r' ', '-', title)
    return str(index).zfill(2) + '-' + title[:59]


# Write section and add matching links at end
def writefile(file_dir, ml, index, text, links):
    newtext = check_links(text, links)
    # print index, ': ', text
    fname = os.path.join(file_dir, make_group(ml, index) + '.md')
    f = open(fname, 'w')
    f.write(newtext)
    f.close()


# Check for any reference to links or footnotes, and add if found
def check_links(text, links):
    linkline = []
    for key, val in sorted(links.iteritems()):
        if key in text:
            linkline.append(val)
    if len(linkline) > 0:
        return text + '\n' + '\n'.join(linkline)
    else:
        return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inpath")
    parser.add_argument("-g", "--groups", dest="groups",
                        type=int, choices=xrange(0, 7), default=0, help="group at")
    parser.add_argument("-l", "--levels", dest="levels", type=int,
                        choices=xrange(1, 7), default=1, help="no of levels")
    args = parser.parse_args()
    main(vars(args))
