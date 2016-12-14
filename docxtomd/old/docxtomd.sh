#!/usr/bin/env bash

# docxtomd.sh
# Hacky script to convert a Word .docx to Markdown
# 
# Copyright (c) 2016 by Adam Twardoch, licensed under Apache 2
# https://github.com/twardoch/markdown-utils
# 
# Pandoc converts .docx to .md well but only extracts media
# which can be .png or .wmf, and links them inside the .md file.
# 
# But .wmf files need to be converted to something else, .svg or .png.
# In this implementation, I use a Java workflow first
# because many .wmf are actually bitmap images, so they're best
# ultimately converted to .png.
# 
# When that workflow fails, I use the libwmf tool which does well
# vectors but not bitmaps :) 
#
# Requires: 
# * perl, bash, Mac OS X
# * pandoc: http://pandoc.org/installing.html
# * Java wmf2svg: https://github.com/hidekatsu-izuno/wmf2svg -- build with 'ant', unzip, move wmf2svg-0.9.8.jar to /usr/local/java
# * Java batik: https://xmlgraphics.apache.org/batik/download.html -- place 'batik' folder in /usr/local/java
# * libwmf wmf2svg: http://wvware.sourceforge.net/libwmf.html or 'brew install libwmf'
#
# If your file is 'mydoc.docx', run 'docxtomd.sh mydoc'

echo "If your file is 'mydoc.docx', run 'convert-docx-to-md.sh mydoc'"

export folder="$1";
export docx="$1.docx";
export md="$1.md";

mkdir "$folder"
cd "$folder"

echo "## Converting docx to md and extracting images into img folder..."
pandoc -s "../$docx" --extract-media=. -t markdown_github -o "$md" >/dev/null
mv "media" "img"

echo "## Patching paths in markdown file..."
perl -pe 's|\(\./media/|(./img/'$folder'_|' < "$md" > "$md.tmp1" && mv "$md.tmp1" "$md"

cd "img"
ls -1 | while read p; do mv "$p" "$folder"_"$p"; done; 

echo "## Converting wmf into svg & png..."
echo "" > ../wmfpng.txt
echo "" > ../wmfsvg.txt

export svgresize=30;

ls -1 *.wmf | while read wmf; do 

	export svg=$(basename "$wmf" .wmf)_wmf.svg;
	export svgbatik=0;

	echo "## Java $wmf to $svg..."
	java -Djava.awt.headless=true -jar /usr/local/java/wmf2svg-0.9.8.jar "$wmf" "$svg"; 

	if [ -f "$svg" ]; then
		export svgbatik=1;
		export png=$(basename "$svg" .svg).png;
		echo "## Batik $svg to $png...";
		java -Djava.awt.headless=true -jar /usr/local/java/batik/batik-rasterizer.jar "$svg"; 
	fi

	if [ -s "$png" ]; then
		export svgbatik=1;
		#rm "$svg";
		echo "$png" >> ../wmfpng.txt;
		perl -pe 's|\.wmf\)|_wmf.png\)|' < "../$md" > "../$md.tmp" && mv "../$md.tmp" "../$md";
	else
		export svgbatik=0;
	fi

	if [[ $svgbatik -eq 0 ]]; then
		#rm "$png";
		#rm "$svg";
		export svgvec=$(basename "$wmf" .wmf)_wmfvec.svg;
		echo "## libwmf $wmf to $svg...";
		wmf2svg -o "$svgvec" "$wmf";
		perl -pe 's|xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"|xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"|' < "$svgvec" > "$svgvec.tmp" && mv "$svgvec.tmp" "$svgvec";
		perl -pe 's|width="(.*?)" height="(.*?)"|"width=\"" . $1*'$svgresize' . "\" height=\"" . $2*'$svgresize' . "\" viewBox=\"0 0 " . $1 . " " . $2 . "\""|e' < "$svgvec" > "$svgvec.tmp" && mv "$svgvec.tmp" "$svgvec";
		perl -pe 's|\.wmf\)|_wmfvec.svg\)|' < "../$md" > "../$md.tmp" && mv "../$md.tmp" "../$md";
	    echo "$svg" >> ../wmfsvg.txt;
	fi

done; 

echo "## Finished creating $folder"

