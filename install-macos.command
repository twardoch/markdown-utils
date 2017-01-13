#!/usr/bin/env bash

dir=${0%/*}
if [ "$dir" = "$0" ]; then
  dir="."
fi
cd "$dir"

# Check if Homebrew is installed
if [ ! -x "$(which brew)" ]; then
	echo "# You must install Homebrew first!"
	open "http://brew.sh/"
	exit 1
fi

# Install pandoc if needed
if [ ! -x "$(which pandoc)" ]; then
	echo "$ brew install pandoc"
	brew install pandoc
else
	echo "# 'pandoc' is installed."
fi 

# Install ant if needed
if [ ! -x "$(which ant)" ]; then
	echo "$ brew install ant"
	brew install ant
else
	echo "# 'ant' is installed."
fi

# Install wmf2svg if needed
if [ ! -e "/usr/local/java/wmf2svg.jar" ]; then
	echo "# Installing 'wmf2svg'..."
	mkdir /usr/local/java
	wget https://github.com/hidekatsu-izuno/wmf2svg/archive/master.zip
	unzip master.zip
	rm master.zip
	cd wmf2svg-master/wmf2svg/
	ant
	mkdir jar
	unzip -o $(ls -1 wmf2svg-*.zip) -d jar
	cd jar
	ls -1 wmf2svg-*.jar | while read p; do 
		cp -f "$p" /usr/local/java;
	done; 
	rm $(ls -1 wmf2svg-*-javadoc.jar)
	rm $(ls -1 wmf2svg-*-sources.jar)
	ln -s /usr/local/java/$(ls -1 wmf2svg-*.jar) /usr/local/java/wmf2svg.jar
	cd ../../../
	rm -rf wmf2svg-master
else
	echo "# 'wmf2svg' is installed."
fi

# Install me
echo "# Installing 'mdutils'"
pip install --user --upgrade -r py-requirements.txt
pip install --user --upgrade .
echo "# Done!"
