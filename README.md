# shk_arbeitszeiten

## usage
- Make the set_chmod.sh file executable:
```
chmod 744 set_chmod.sh
```
- Execute set_chmod.sh:
```
./set_chmod.sh
```

## notes
- Works best with apache2 on linux
- script_python2.py for compatibility with python2, this version works with 2.7.18
- script.py needs python 3.10
- due to incompetence on whoevers part, the pdf is completely fucked up in many places
- we weren't able to find the exact issue, only solution was to yeet it through pdftk -.-
- now the installed java on the server is broken too, therefore the pdftk-java-port can't be used
- because just trying to compile from source was a pain in the ass (libgcj libgcj-devel: https://en.wikipedia.org/wiki/GNU_Compiler_for_Java, whatever), we grabbed a precompiled version from the first github we found


## credits
- TU Dresden for "hosting" this awesome service <3
- Zentrale Universitätsverwaltung der TU Dresden for fucking up PDF
- ZIH Dresden for fucking up Java
- PDFLabs for developing the latest release of pdftk 9 years ago
