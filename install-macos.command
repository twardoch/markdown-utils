#!/usr/bin/env bash

dir=${0%/*}
if [ "$dir" = "$0" ]; then
  dir="."
fi
cd "$dir"

# Check if brew is installed
if [ ! -x "$(which brew)" ]; then
	echo "# Installing 'brew'..."
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
else
	echo "# Updating 'brew'..."
	brew update
fi

# Install pandoc if needed
if [ ! -x "$(which pandoc)" ]; then
	echo "$ brew install pandoc"
	brew install pandoc
else
	echo "$ brew upgrade pandoc && brew cleanup pandoc"
	brew upgrade pandoc && brew cleanup pandoc
fi

# Install ant if needed
if [ ! -x "$(which ant)" ]; then
	echo "$ brew install ant"
	brew install ant
else
	echo "$ brew upgrade ant && brew cleanup ant"
	brew upgrade ant && brew cleanup ant
fi

# Install wmf2svg if needed
if [ ! -e "/usr/local/java/wmf2svg.jar" ]; then
	echo "# Installing 'wmf2svg'..."
	mkdir -p /usr/local/java
	wget https://github.com/hidekatsu-izuno/wmf2svg/archive/master.zip
	unzip master.zip
	rm master.zip
	cd wmf2svg-master/
	chmod gou+x gradlew
	cp ../gradle.properties .
	echo "sourceCompatibility = 11" >> build.gradle
	echo "targetCompatibility = 11" >> build.gradle
	./gradlew jar -i
	cd build/libs
	ls -1 wmf2svg-*.jar | while read p; do
		cp -f "$p" /usr/local/java;
	done;
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
