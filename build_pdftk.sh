#!/usr/bin/sh

# get sources
wget https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/pdftk-2.02-src.zip

# unzip sources
unzip pdftk-2.02-src.zip

# delete zip
pdftk-2.02-src.zip

# change to source-dir
cd pdftk-2.02-dist/pdftk

# set correct gcc-version
sed -i s/4.3/4.8/g Makefile.Suse